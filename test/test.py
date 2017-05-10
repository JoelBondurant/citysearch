#!/usr/bin/env python3
"""
Module to test city api.
"""

import timeit
import unittest as ut

import requests


BASEURL = 'http://127.0.0.1:8080/v0/city/'

def url(txt):
	return BASEURL+txt

def fetch(txt, raw = False):
	rawr = requests.get(url(txt))
	if not raw:
		rawr = rawr.json()
	return rawr


class APITest(ut.TestCase):

	def setUp(self):
		self.started = timeit.default_timer()
		print('.')

	def tearDown(self):
		elapsed = timeit.default_timer() - self.started
		print('time: %s sec.' % elapsed)

	def test_count1(self):
		cnt = fetch('count')['count']
		print('city count: %s' % cnt)
		self.assertTrue(cnt > 142310)

	def test_count2(self):
		n = 100
		t = timeit.timeit(lambda: fetch('count')['count'], number = n)
		print('count rate: %s/sec' % str(n/t))
		self.assertTrue(n/t > 10)

	def test_proximity1(self):
		cities = fetch('proximity_search?name=Daly%20City&k=6')
		GEONAMEIDS = [5341430, 5330854, 5338703, 5330810, 5397765, 5391959]
		geonameids = [c['geonameid'] for c in cities]
		print('proximity search matches: %s/%s' % (len(geonameids), len(GEONAMEIDS)))
		self.assertTrue(set(GEONAMEIDS) == set(geonameids))

	def test_proximity2(self):
		n = 100
		t = timeit.timeit(lambda: fetch('proximity_search?name=Daly%20City&k=6'), number = n)
		print('proximity rate: %s/sec' % str(n/t))
		self.assertTrue(n/t > 10)

	def test_text1(self):
		cities = fetch('text_search?q=San%20Francisco')
		GEONAMEIDS = [3429054, 3837624, 3837625, 3449112, 3493146, 2511381, 3590197, 3590213, 3590219, 3600338]
		GEONAMEIDS += [3602272, 3514409, 3517989, 3519251, 3519256, 3519282, 3986971, 5391959, 5454711, 5490263]
		geonameids = [c['geonameid'] for c in cities]
		print('text search matches: %s/%s' % (len(geonameids), len(GEONAMEIDS)))
		self.assertTrue(set(GEONAMEIDS) == set(geonameids))

	def test_text2(self):
		n = 100
		t = timeit.timeit(lambda: fetch('text_search?q=San%20Francisco'), number = n)
		print('text rate: %s/sec' % str(n/t))
		self.assertTrue(n/t > 10)



if __name__ == '__main__':
	ut.main()
