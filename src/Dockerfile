# Container image for CitySearch web api.
FROM python:3.6.1
ENV TERM screen-256color

# Add basic dependencies:
RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y build-essential gcc g++ python3-dev
RUN apt-get install -y mariadb-client-10.0 libmysqlclient-dev

# Add Python extras:
RUN pip install -U pip \
	&& pip install -U cython numpy pandas \
	&& pip install -U requests sanic \
	&& pip install -U mysqlclient

RUN pip install -U ipython ipdb sqlalchemy
RUN apt-get install -y vim less

EXPOSE 8080
COPY . /usr/local/citysearch/
WORKDIR /usr/local/citysearch
CMD ["/usr/local/citysearch/webapi.py"]
