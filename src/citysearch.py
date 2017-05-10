"""
A city search module.
"""

import io
import os
import re
import time
import zipfile
import functools

import requests
import numpy as np
import pandas as pd

import logger
from mariadb import SQL
from sphinxql import SphinxQL



### DATA LOADING ###

def dlpath():
	""" Download path."""
	return '/tmp/citysearch'


def srcfile():
	""" Full source file path."""
	return os.path.join(dlpath(), 'cities1000.txt')


def download():
	""" Download city data from web source."""
	logger.info('Download starting...')
	if os.path.isfile(srcfile()):
		logger.info('Using cache.')
	else:
		zurl = 'http://download.geonames.org/export/dump/cities1000.zip'
		rz = requests.get(zurl)
		zf = zipfile.ZipFile(io.BytesIO(rz.content))
		zf.extractall(dlpath())
	logger.info('Download finished.')


def colnames():
	""" Column name list from download.geonames.org/export/dump. """
	colnames = ['geonameid','name','asciiname','altnames','latitude','longitude','feat_class','feat_code']
	colnames += ['country_code', 'cc2', 'admin1_code', 'admin2_code', 'admin3_code', 'admin4_code']
	colnames += ['population','elevation','dem','timezone','modified']
	return colnames


def colset():
	""" A set for the column names for faster column checks. """
	return set(colnames())


def to_dataframe():
	""" Parse csv with Pandas. """
	cols = colnames()
	df = pd.read_csv(srcfile(), sep = '\t', header = None, names = cols, index_col = False, low_memory = False)
	df = df.astype(object).where(pd.notnull(df), None)
	df.latitude = df.latitude.astype('float32')
	df.longitude = df.longitude.astype('float32')
	#df.population = df.population.astype('uint64')
	#df.elevation = df.elevation.astype('float32')
	df.reset_index(drop = False, inplace = True)
	df.rename(columns = {'index':'id'}, inplace = True)
	df.id = df.id + 1 # Sphinx doesnt like 0 based indexing
	assert df.shape[1] == len(cols) + 1
	return df


def sphinx_escape(astr):
	""" Sphinx needs help escaping strings."""
	if type(astr) != str:
		return astr
	return re.sub(r"([=\(\)|\-!@~\"&/\\\^\$\=])", r"\\\1", astr)


def to_sphinx(df):
	""" Defer the city altnames to Sphinx. """
	logger.info('Inserting city altnames to Sphinx.')
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
		logger.info('Data exists, skipping.')
	logger.info('Finished Sphinx inserts.')


def to_mariadb(df):
	""" Load city data into MariaDB. """
	logger.info('Loading city data into MariaDB...')
	sql = SQL(db = 'mysql')
	sql.execute('CREATE DATABASE IF NOT EXISTS citysearch;')
	sql.execute('USE citysearch;')
	try:
		numrecs = int(sql.fetchone('SELECT COUNT(1) FROM citysearch.City;')[0])
	except:
		numrecs = 0
	if numrecs == 0:
		sqlsrc = ['City.sql','Haversine.sql','GeoDist.sql','ProximitySearch.sql']
		for src in sqlsrc:
			with open('./'+src,'r') as fin:
				sqltxt = fin.read()
			sql.execute_ddl(sqltxt)
			sql.commit()
		sqltxt = sql.generate_insert('City', df.columns.tolist())
		vals = df.to_records(index = False)
		vals = [tuple(x) for x in vals] # < mariadb driver expectations
		sql.executemany(sqltxt, vals)
		sql.commitclose()
	else:
		logger.info('Data exists, skipping.')
	logger.info('Finished loading city data into MariaDB.')


def bootstrap():
	""" Bootstrap the citysearch app. """
	logger.info('Bootstrapping CitySearch...')
	download()
	df = to_dataframe()
	to_sphinx(df)
	df.altnames = df.altnames.str[:200]
	to_mariadb(df)
	time.sleep(1)
	logger.info('CitySearch data is loaded.')
	return df



### Realtime API ###

class CityAPI:
	
	def __init__(self):
		""" Load data into databases and cache."""
		time.sleep(4) # Wait a sec for databases...
		df = bootstrap()
		self.df = df
		self.df_geonameid = df.set_index('geonameid')


	def keyval_search(self, akey, avalue, country_code = None):
		""" Base city lookup. """
		if akey not in colset():
			return None # No SQL injection here.
		if akey == 'geonameid':
			return int(df.geonameid.loc[avalue].id)
		try:
			sql = SQL.singleton()
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
		sql = SQL.singleton()
		params = (city_id, k, country_code)
		rs = sql.fetchproc(sqltxt, params, jsonify = True)
		return rs


	def text_search(self, atext):
		""" SphinxQL based text search. """
		spx = SphinxQL.singleton()
		atext = sphinx_escape(atext)
		city_ids = spx.fetchall("SELECT id FROM rt WHERE MATCH('"+atext+"')")
		city_ids = [str(int(x[0])) for x in city_ids] # Ensure these are safe.
		city_ids = ','.join(city_ids)
		sql = SQL.singleton()
		rs = sql.fetchall('SELECT * FROM City WHERE id IN ('+city_ids+');', jsonify = True)
		return rs

