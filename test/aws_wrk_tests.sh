#!/usr/bin/env bash
# Run wrk tests.
echo 'Starting wrk tests.'
echo ''
wrk -c 100 -d 10 -t 33 "http://citysearch:8080/v0/city/hello"
echo ''
wrk -c 100 -d 10 -t 33 "http://citysearch:8080/v0/city/count"
echo ''
wrk -c 100 -d 10 -t 33 "http://citysearch:8080/v0/city/proximity_search?name=Daly%20City&k=10"
echo ''
wrk -c 100 -d 10 -t 33 "http://citysearch:8080/v0/city/proximity_search2?name=Daly%20City&k=10"
echo ''
wrk -c 100 -d 10 -t 33 "http://citysearch:8080/v0/city/text_search?q=San%20Francisco"
echo ''
echo 'Finished wrk tests.'
