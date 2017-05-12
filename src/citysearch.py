"""
A city search module.
This module has mixed concerns about data fetching,
database schema, database inserts, web caching, and web responses.
"""

import io
import os
import re
import time
import random
import zipfile
import concurrent.futures

import requests
import numpy as np
import pandas as pd
from rtree import index as rtree

import logger
from mariadb import SQL
from sphinxql import SphinxQL


# Statics:
col_names = ['geonameid','name','asciiname','altnames','latitude','longitude','feat_class','feat_code']
col_names += ['country_code', 'cc2', 'admin1_code', 'admin2_code', 'admin3_code', 'admin4_code']
col_names += ['population','elevation','dem','timezone','modified']
col_set = set(col_names)


def colnames():
	""" Column name list from download.geonames.org/export/dump. """
	return col_names

def colset():
	""" A set for the column names for faster column checks. """
	return col_set

def sphinx_escape(astr):
	""" Sphinx needs help escaping strings."""
	if type(astr) != str:
		return astr
	return re.sub(r"([=\(\)|\-!@~\"&/\\\^\$\=])", r"\\\1", astr)

def chunks(l, n):
	"""Yield successive n-sized chunks from l."""
	for i in range(0, len(l), n):
		yield l[i:i + n]



class DataLoader:

	def dlpath(self):
		""" Download path."""
		return '/tmp/citysearch'

	def srcfile(self):
		""" Full source file path."""
		return os.path.join(self.dlpath(), 'cities1000.txt')

	def download(self):
		""" Download city data from web source."""
		logger.info('Download starting...')
		if os.path.isfile(self.srcfile()):
			logger.info('City csv exists, skipping donwload...')
		else:
			zurl = 'http://download.geonames.org/export/dump/cities1000.zip'
			rz = requests.get(zurl)
			zf = zipfile.ZipFile(io.BytesIO(rz.content))
			zf.extractall(self.dlpath())
		logger.info('Download finished.')

	def to_dataframe(self):
		""" Parse csv with Pandas. """
		cols = colnames()
		df = pd.read_csv(self.srcfile(), sep = '\t', header = None, names = cols, index_col = False, low_memory = False)
		df = df.astype(object).where(pd.notnull(df), None)
		df.latitude = df.latitude.astype('float32')
		df.longitude = df.longitude.astype('float32')
		#df.population = df.population.astype('uint64')
		#df.elevation = df.elevation.astype('float32')
		df.index = df.index + 1 # Use 1 based indexing.
		df.reset_index(drop = False, inplace = True)
		df.rename(columns = {'index':'id'}, inplace = True)
		assert df.shape[1] == len(cols) + 1
		return df

	def to_sphinx(self, df):
		""" Defer the city altnames to Sphinx. """
		logger.info('Inserting city data into Sphinx...')
		dg = df[['id','altnames']].copy()
		dg = dg[~dg.altnames.isnull()]
		dg.altnames = dg.altnames.apply(sphinx_escape)
		dg['pk'] = dg.id
		dm = dg.as_matrix()
		sql = SphinxQL()
		numrecs = int(sql.fetchone('SELECT COUNT(*) FROM rt')[0])
		if numrecs == 0:
			sqltxt = 'INSERT INTO rt VALUES (%s, %s, %s)'
			for x in dm:
				params = tuple(x.tolist())
				sql.execute(sqltxt, params)
			sql.commitclose()
		else:
			logger.info('Sphinx data exists, skipping.')
		logger.info('Finished Sphinx inserts.')

	def ddl_mariadb(self):
		""" Throw DDL at MariaDB. """
		logger.info('Preparing MariaDB DDL...')
		printsql = False
		sql_zero = lambda: SQL(db = 'mysql', printsql = printsql, autocommit = True, autoretry = False)
		sql_zero().execute_ddl('CREATE DATABASE IF NOT EXISTS citysearch;')
		time.sleep(2)
		sql_ddl = lambda: SQL(printsql = printsql, autocommit = True, autoretry = False)
		try:
			numrecs = int(sql_ddl().fetchone('SELECT COUNT(1) FROM citysearch.City;')[0])
		except:
			numrecs = 0
		if numrecs == 0:
			sqlsrc = ['Start.sql','City.sql','Haversine.sql','GeoDist.sql','ProximitySearch.sql']
			for src in sqlsrc:
				with open('./'+src,'r') as fin:
					sqltxt = fin.read()
				for sqltxt_part in sqltxt.split('#split#'):
					if sqltxt_part.strip() != '':
						sql_ddl().execute_ddl(sqltxt_part)
			time.sleep(2)
		logger.info('MariaDB DDL applied.')

	def to_mariadb(self, df):
		""" Load city data into MariaDB. """
		logger.info('Inserting city data into MariaDB...')
		sql = lambda: SQL(printsql = False, autocommit = False, autoretry = True)
		try:
			numrecs = int(sql().fetchone('SELECT COUNT(1) FROM citysearch.City;')[0])
		except:
			numrecs = 0
		if numrecs == 0:
			sqltxt = SQL.generate_insert('City', df.columns.tolist())
			vals = df.to_records(index = False)
			vals = [tuple(x) for x in vals] # < mariadb driver expectations
			batch_size = 10000
			sqlconn = sql()
			for chunk in chunks(vals, batch_size):
				sqlconn.executemany(sqltxt, chunk)
			sqlconn.commitclose()
		else:
			logger.info('MariaDB data exists, skipping.')
		logger.info('Finished MariaDB inserts.')

	def persist(self):
		logger.info('City data persistence started.')
		self.ddl_mariadb()
		df_mdb = self.to_dataframe()
		df_spx = df_mdb[['id','altnames']].copy()
		df_mdb.altnames = df_mdb.altnames.str[:200]
		with concurrent.futures.ThreadPoolExecutor(max_workers = 2) as ex:
			ex.submit(self.to_mariadb, df_mdb)
			ex.submit(self.to_sphinx, df_spx)
		logger.info('City data persistence finished.')
		return df_mdb


def bootstrap():
	""" Bootstrap the citysearch app. """
	logger.info('Bootstrapping CitySearch...')
	dl = DataLoader()
	dl.download()
	logger.info('Waiting a second for databases...')
	time.sleep(8)
	webcache = dl.persist()
	logger.info('Bootstrapping is complete.')
	return webcache



### Realtime API ###

class CityAPI:
	
	def __init__(self):
		""" Load data into databases and cache."""
		time.sleep(4) # Wait a sec for databases...
		df = bootstrap()
		logger.info('Generating cache indexes...')
		self.df = df
		self.df_geonameid = df.set_index('geonameid')[['id']]
		self.df_name = df.set_index('name')[['id']]
		geoslice = df[['id','longitude','latitude']]
		rgeo = rtree.Rtree()
		for i in range(1, len(geoslice)):
			rgeo.insert(i, tuple(geoslice.iloc[i][1:].tolist()))
		self.rgeo = rgeo # geographic index
		self.df_coords = geoslice.set_index('id')
		#self.df = None # Drop unused bulk.
		logger.info('Cache index generation complete.')


	def city_coords(self, city_id):
		""" Get city coordinates from city_id."""
		return self.df_coords.loc[city_id].tolist()


	def keyval_search(self, akey, avalue, country_code = None):
		""" Base city lookup. """
		if akey not in colset():
			return None # No SQL injection here.
		if akey == 'geonameid':
			return int(self.df_geonameid.loc[avalue].id)
		if akey == 'name' and country_code and len(country_code) == 2:
			return int(self.df_name[self.df_name.country_code == country_code].loc[avalue].id)
		elif akey == 'name':
			return int(self.df_name.loc[avalue].id)
		try:
			sql = SQL.singleton(random.randint(0,16))
			if country_code:
				sqltxt = 'SELECT id FROM City WHERE '+akey+' = %s and country_code = %s;'
				city_id = int(sql.fetchone(sqltxt, (avalue, country_code))[0])
			else:
				sqltxt = 'SELECT id FROM City WHERE '+akey+' = %s;'
				city_id = int(sql.fetchone(sqltxt, avalue)[0])
		except:
			city_id = None
		return city_id


	def proximity_search(self, akey, avalue, k, country_code = None):
		""" MariaDB based proximity search. """
		if akey not in colset():
			return {}
		if country_code and len(country_code) != 2:
			return {}
		k = int(k)
		city_id = self.keyval_search(akey, avalue, country_code)
		sqltxt = 'proximity_search'
		sql = SQL.singleton(random.randint(0,16))
		params = (city_id, k, country_code)
		rs = sql.fetchproc(sqltxt, params, jsonify = True)
		return rs[:-1][0]


	def proximity_search2(self, akey, avalue, k, country_code = None):
		""" RTree+MariaDB based proximity search. """
		if akey not in colset():
			return {}
		if country_code and len(country_code) != 2:
			return {}
		k = int(k)
		city_id = self.keyval_search(akey, avalue, country_code)
		coords = self.city_coords(city_id)
		rs = self.df.loc[self.rgeo.nearest(coords, k)].to_json(orient = 'values')
		return rs


	def text_search(self, atext):
		""" SphinxQL based text search. """
		spx = SphinxQL()
		atext = sphinx_escape(atext)
		city_ids = spx.fetchall("SELECT id FROM rt WHERE MATCH('"+atext+"')")
		city_ids = [str(int(x[0])) for x in city_ids] # Ensure these are safe.
		city_ids = ','.join(city_ids)
		sql = SQL.singleton(random.randint(0,16))
		rs = sql.fetchall('SELECT * FROM City WHERE id IN ('+city_ids+');', jsonify = True)
		return rs

