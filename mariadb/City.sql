USE test;

CREATE TABLE IF NOT EXISTS City (
	id MEDIUMINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
	geonameid INT UNSIGNED NOT NULL,
	name CHAR(100) NOT NULL COLLATE utf8_bin,
	asciiname CHAR(100) COLLATE utf8_bin,
#	alternatenames TEXT COLLATE utf8_bin,
	latitude FLOAT NOT NULL,
	longitude FLOAT NOT NULL,
	feat_class CHAR(1) NOT NULL COLLATE utf8_bin,
	feat_code CHAR(5) NOT NULL COLLATE utf8_bin,
	country_code CHAR(2) COLLATE utf8_bin,
	cc2 CHAR(5) COLLATE utf8_bin,
	admin1_code CHAR(10) NOT NULL COLLATE utf8_bin,
	admin2_code CHAR(50) NOT NULL COLLATE utf8_bin,
	admin3_code CHAR(10) NOT NULL COLLATE utf8_bin,
	admin4_code CHAR(20) NOT NULL COLLATE utf8_bin,
	population INT UNSIGNED NOT NULL,
	elevation FLOAT,
	dem SMALLINT NOT NULL,
	timezone CHAR(32) COLLATE utf8_bin,
	modified DATE,
	INDEX (latitude, longitude)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
