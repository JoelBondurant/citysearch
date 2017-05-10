#!/usr/bin/env bash
docker stop citysearch
docker rm citysearch
docker run --rm -it --name citysearch -v /tmp/citysearch:/tmp/citysearch --link mariadb:mariadb --link sphinx:sphinx citysearch webapi
docker logs citysearch -f --tail=10
