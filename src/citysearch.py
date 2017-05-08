"""
A city search module.
"""

import io
import os
import time
import zipfile

import requests
import pandas as pd


def dlpath():
	""" Download path, defaults to '.', may be set with environment variable $CITYSEARCH_DLPATH."""
	return os.getenv('CITYSEARCH_DLPATH', './data')


def download():
	""" Download city data from web source."""
	print('Download starting...')
	zurl = 'http://download.geonames.org/export/dump/cities1000.zip'
	rz = requests.get(zurl)
	zf = zipfile.ZipFile(io.BytesIO(rz.content))
	zf.extractall(os.path.join(dlpath()))
	print('Download finished.')


def colnames():
	""" Column name list from download.geonames.org/export/dump. """
	colnames = ['geonameid','name','asciiname','alternatenames','latitude','longitude','feat_class','feat_code']
	colnames += ['country_code', 'cc2', 'admin1_code', 'admin2_code', 'admin3_code', 'admin4_code']
	colnames += ['population','elevation','dem','timezone','modified']
	return colnames


def to_dataframe():
	""" Parse csv with Pandas. """
	cols = colnames()
	fp = os.path.join(dlpath(), 'cities1000.txt')
	df = pd.read_csv(fp, sep = '\t', header = None, names = cols, index_col = False, low_memory = False)
	df.latitude = df.latitude.astype('float32')
	df.longitude = df.longitude.astype('float32')
	df.population = df.population.astype('uint64')
	df.elevation = df.elevation.astype('float32')
	df.admin1_code = df.admin1_code.astype(str)
	df.admin2_code = df.admin2_code.astype(str)
	df.admin3_code = df.admin3_code.astype(str)
	df.admin4_code = df.admin4_code.astype(str)
	assert df.shape[1] == len(cols)
	return df

def haversine(lat1, lon1, lat2, lon2):
	""" Exact geo distance. """
	

def df_search():
	return None
