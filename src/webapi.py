#!/usr/bin/env python3

import os

from sanic import Sanic
from sanic.response import json

import logger
from citysearch import CityAPI


cityapi = CityAPI()
webapi = Sanic()

@webapi.route('/v0/city/kvsearch')
async def kvsearch(req):
	akey = list(req.args.keys())[0]
	avalue = list(req.args.values())[0]
	rs = cityapi.keyval_search2(akey, avalue)
	return json(rs)


@webapi.route('/v0/city/proximity_search')
async def proximity_search(req):
	req.args['akey'] # ? Not a clue how to debug this, sanic+numpy=fail.
	cityapi.proximity_search()
	return json({'hello':'proximity'})


def main():
	logger.info('CitySearch webapi started.')
	workers = (os.cpu_count() * 3) // 4 + 1
	webapi.run(host = '0.0.0.0', port = 8080, workers = workers, debug = False)
	logger.info('CitySearch webapi stopped.')


if __name__ == '__main__':
	main()
