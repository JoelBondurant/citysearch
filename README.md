# citysearch
Example API for searching cities.

Demo at: 13.56.10.58

The endpoints for searching cities is:

1) hello, this endpoint is for basic connectivity verification and baseline performance benchmarking.
  pattern: http://citysearch:8080/v0/city/hello

ex> curl http://citysearch:8080/v0/city/hello
{"hello":"world"}

2) count, skip the cache and hit the database for city count.
  pattern: http://citysearch:8080/v0/city/count

ex> curl http://citysearch:8080/v0/city/count
{"count":142315}

3) proximity_search, takes 1 key=value positional argument in the query parameters to fetch the origin city,
  also accepts optional values k and ccode for the number of results and country code.
  pattern: http://citysearch:8080/v0/city/proximity_search?a_key=a_urlsafe_value[&k=number_of_results][&ccode=country_code]
  
ex> curl http://citysearch:8080/v0/city/proximity_search?name=Daly%20City&k=10
...

4) text_search, Defers full text searching of city fields to SphinxSearch, see their docs for full capabilites.
  pattern: http://citysearch:8080/v0/city/text_search?q=query_text
  
ex> curl http://citysearch:8080/v0/city/text_search?q=San%20Francisco
...

