# Container image for CitySearch web api.
FROM python:3.6.1
ENV TERM screen-256color

# Add basic dependencies:
RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y build-essential gcc g++ python3-dev
RUN apt-get install -y mariadb-client-10.0 libmysqlclient-dev vim less

# Add Python extras:
RUN pip install -U pip \
	&& pip install -U cython numpy pandas ipython ipdb \
	&& pip install -U requests sanic aiohttp aiodns \
	&& pip install -U sqlalchemy mysqlclient aiomysql \
	&& pip install -U cachetools aiocache

EXPOSE 8080
COPY . /usr/local/citysearch/
RUN ln -s /usr/local/citysearch/webapi.py /usr/bin/webapi
WORKDIR /usr/local/citysearch
CMD ["webapi"]
