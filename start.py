#!/usr/bin/env python3

import os
import sys
import getpass
import argparse
import subprocess as sp


DEFAULT_PASSWORD = 'citysearch123456'


def pre_start(cname, args):
	CONTAINER_NAME = cname
	container_name = cname.lower()
	if args.restart:
		print('%s restarting...' % CONTAINER_NAME)
		sp.call(['docker', 'restart', container_name])
		sys.exit(0)
	if args.clean or args.stop:
		print('%s stopping...' % CONTAINER_NAME)
		sp.call(['docker', 'stop', container_name])
		if args.clean:
			print('%s process removal...' % CONTAINER_NAME)
			sp.call(['docker', 'rm', container_name])
		if args.stop:
			sys.exit(0)


def start_mariadb(args):
	cname = 'MariaDB'
	CONTAINER_NAME = cname
	container_name = cname.lower()
	pre_start(cname, args)
	PROMPT = 'Enter %s: '
	if args.prompt:
		sqlRootPass = getpass.getpass(PROMPT % 'SQL_ROOT_PASS')
	else:
		print('%s reading environment variables...' % CONTAINER_NAME)
		sqlRootPass = os.getenv('SQL_ROOT_PASS', DEFAULT_PASSWORD)
	print('%s starting...' % CONTAINER_NAME)
	startCmd = 'docker run '
	startCmd += '--name=%s ' % container_name
	startCmd += '-h %s ' % container_name
	startCmd += '--restart=always '
	startCmd += '-p 3306:3306 '
	startCmd += ('-e "%s=%s" ' % ('MYSQL_ROOT_PASSWORD', sqlRootPass))
	startCmd += '-d %s' % container_name
	if args.new:
		if args.echo:
			print('Start cmd:\n' + startCmd)
		sp.call(startCmd, shell = True)
	else:
		sp.call(['docker','start',container_name])
	print('%s started.' % CONTAINER_NAME)


def start_sphinx(args):
	cname = 'Sphinx'
	CONTAINER_NAME = cname
	container_name = cname.lower()
	pre_start(cname, args)
	print('%s starting...' % CONTAINER_NAME)
	startCmd = 'docker run '
	startCmd += '--name=%s ' % container_name
	startCmd += '-h %s ' % container_name
	startCmd += '--restart=always '
	startCmd += '-d %s' % container_name
	if args.new:
		if args.echo:
			print('Start cmd:\n' + startCmd)
		sp.call(startCmd, shell = True)
	else:
		sp.call(['docker','start',container_name])
	print('%s started.' % CONTAINER_NAME)


def main():
	""" Main entry point to start. """
	desc = """Service start manager, Docker-Compose is still a mess."""
	ap = argparse.ArgumentParser(add_help = True, description = desc)
	ap.add_argument('-c', '--clean', action = 'store_true', default = False, help = 'Clean process start.')
	ap.add_argument('-e', '--echo', action = 'store_true', default = False, help = 'Echo start command.')
	ap.add_argument('-n', '--new', action = 'store_true', default = True, help = 'New process run.')
	ap.add_argument('-p', '--prompt', action = 'store_true', default = False, help = 'Prompt for secrets.')
	ap.add_argument('-r', '--restart', action = 'store_true', default = False, help = 'Restart process.')
	ap.add_argument('-s', '--stop', action = 'store_true', default = False, help = 'Stop process.')
	args = ap.parse_args()
	#start_mariadb(args)
	start_sphinx(args)
	#start_citysearch(args)


if __name__ == '__main__':
	main()

