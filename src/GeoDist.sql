DROP FUNCTION IF EXISTS geo_dist;
#split#
CREATE FUNCTION geo_dist(lat1 FLOAT, lon1 FLOAT, lat2 FLOAT, lon2 FLOAT) RETURNS FLOAT
	NO SQL DETERMINISTIC
	COMMENT 'Returns the distance in kilometers on the Earth
			between two known points of latitude and longitude
			measured in degrees.'
BEGIN
	RETURN 6371.0088 * haversine(radians(lat1), radians(lon1), radians(lat2), radians(lon2));
END;

