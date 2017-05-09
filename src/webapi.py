#!/usr/bin/env python3

import os

from sanic import Sanic
from sanic.response import json

import logger
from mariadb import SQL
from citysearch import CityAPI


cityapi = CityAPI()
webapi = Sanic()


@webapi.route('/v0/city/hello')
async def hello(req):
	'''
	Hello api endpoint for testing.
	example:
	http://citysearch:8080/v0/city/hello
	'''
	return json({'hello':'world'})


@webapi.route('/v0/city/count')
async def count(req):
	'''
	City count endpoint:
	example:
	http://citysearch:8080/v0/city/count
	'''
	cnt = SQL.singleton().fetchone('select count(1) from City;')[0]
	return json({'count':cnt})



@webapi.route('/v0/city/proximity_search')
async def proximity_search(req):
	'''
	Proximity search for cities:
	The city identifier/value pair should be provided as the first 
	positional query parameter. Limit the city count with query 
	parameter k (defaults to 10). Limit the country in the origin 
	and result set queries with query parameter ccode.
	example:
	http://citysearch:8080/v0/city/proximity_search?name=Daly%20City&k=10
	http://citysearch:8080/v0/city/proximity_search?geonameid=3039154&k=100&ccode=US
	'''
	akey = list(req.args.keys())[0]
	avalue = list(req.args.values())[0][0]
	if 'k' in req.args:
		k = int(req.args['k'][0])
	else:
		k = 10
	if 'ccode' in req.args:
		ccode = req.args['ccode'][0]
	else:
		ccode = None
	rs = cityapi.proximity_search(akey, avalue, k, ccode)
	return json(rs)


def main():
	logger.info('CitySearch webapi started.')
	workers = (os.cpu_count() * 3) // 4 + 1
	webapi.run(host = '0.0.0.0', port = 8080, workers = workers, debug = False)
	logger.info('CitySearch webapi stopped.')


if __name__ == '__main__':
	main()
