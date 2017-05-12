#!/usr/bin/env bash
# Run wrk tests.
echo 'Starting wrk tests.'
wrk -c 64 -d 10 -t 32 "http://127.0.0.1:8080/v0/city/hello"
wrk -c 64 -d 10 -t 32 "http://127.0.0.1:8080/v0/city/count"
wrk -c 64 -d 10 -t 32 "http://127.0.0.1:8080/v0/city/proximity_search?name=Daly%20City&k=10"
wrk -c 64 -d 10 -t 32 "http://127.0.0.1:8080/v0/city/proximity_search2?name=Daly%20City&k=10"
wrk -c 64 -d 10 -t 32 "http://127.0.0.1:8080/v0/city/text_search?q=San%20Francisco"
echo 'Finished wrk tests.'
