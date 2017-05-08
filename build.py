#!/usr/bin/env python3

import os
import random
import argparse
import subprocess as sp


def build(cname, args):
	CONTAINER_NAME = cname
	container_name = CONTAINER_NAME.lower()
	if container_name == 'citysearch':
		os.chdir('src')
	else:
		os.chdir(container_name)
	print('%s build started.' % CONTAINER_NAME)
	if args.clean:
		print('%s clean-up...' % CONTAINER_NAME)
		sp.call(['docker', 'stop', container_name])
		sp.call(['docker', 'rm', container_name])
		sp.call(['docker', 'rmi', container_name])
	if args.break_cache:
		with open('.breakcache', 'w') as fout:
			fout.write(str(random.randint(0, 10**10)))
	else:
		sp.call(['touch', '.breakcache'])
	build_args = ['docker', 'build', '--tag=%s' % container_name]
	if args.no_cache:
		build_args += ['--no-cache=true']
	sp.call(build_args + ['.'])
	os.chdir('..')
	print('%s build complete.\n\n' % CONTAINER_NAME)


def main():
	desc = """Build Application:  
	Builds docker containers for CitySearch api and MariaDB."""
	argparser = argparse.ArgumentParser(description = desc, add_help = True)
	argparser.add_argument('-c', '--clean', action = 'store_true', default = False, help = 'Clean build.')
	argparser.add_argument('-b', '--break_cache', action = 'store_true', default = False, help = 'Break cache.')
	argparser.add_argument('-n', '--no_cache', action = 'store_true', default = False, help = 'No cache.')
	args = argparser.parse_args()
	build('MariaDB', args)
	build('Sphinx', args)
	build('CitySearch', args)

if __name__ == '__main__':
	main()

