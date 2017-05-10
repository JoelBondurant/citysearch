DROP FUNCTION IF EXISTS haversine;

CREATE FUNCTION haversine(lat1 FLOAT, lon1 FLOAT, lat2 FLOAT, lon2 FLOAT) RETURNS FLOAT
	NO SQL DETERMINISTIC
	COMMENT 'Returns the distance in radians on a sphere
			 between two known points of latitude and longitude
			 measured in radians.'
BEGIN
	RETURN ACOS(COS(lat1) * COS(lat2) * COS(lon2 - lon1) + SIN(lat1) * SIN(lat2));
END;

