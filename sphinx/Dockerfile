# SphinxSearch Dockerfile

FROM ubuntu:17.04

ENV TERM screen-256color
EXPOSE 9306 9312

RUN apt-get update
RUN apt-get install -y sphinxsearch mysql-client libmysqlclient-dev
COPY sphinx.conf /etc/sphinxsearch/

ADD city_altnames.tsv /
RUN mkdir /var/lib/sphinxsearch/data/citysearch

ADD searchd.sh /
RUN chmod a+x searchd.sh
CMD ["/searchd.sh"]
