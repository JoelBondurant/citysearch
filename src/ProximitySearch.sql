DROP PROCEDURE IF EXISTS proximity_search;
#split#
CREATE PROCEDURE proximity_search (IN city_id INT UNSIGNED, k INT UNSIGNED, ccode CHAR(2))
BEGIN
	SELECT @lat := latitude, @lon := longitude FROM City WHERE id = city_id;
	IF k < 1000 THEN
		SET @dt := 2;
	ELSE
		SET @dt := LEAST(180, 30*LOG(3, k+1)+1);
	END IF;
	CREATE TEMPORARY TABLE IF NOT EXISTS GeoPatch (id INT UNSIGNED) ENGINE = MEMORY;
	TRUNCATE GeoPatch;
	# North Pole:
	IF @lat > 80 THEN
		INSERT INTO GeoPatch
		SELECT id FROM City WHERE latitude >= (80 - 4*@dt) AND latitude <= 90;
	# South Pole:
	ELSEIF @lat < -80 THEN
		INSERT INTO GeoPatch
		SELECT id FROM City WHERE latitude >= -90 AND latitude <= (-80 + 4*@dt);
	# Prime Meridian:
	ELSEIF (@lon + @dt) > 180 OR (@lon - @dt) < -180 THEN
		INSERT INTO GeoPatch
		SELECT id FROM City WHERE latitude >= (@lat - @dt) AND latitude <= (@lat + @dt) AND (longitude <= (-180 + @dt) OR longitude >= (180 - @dt));
	ELSE
		INSERT INTO GeoPatch
		SELECT id FROM City WHERE latitude >= (@lat - @dt) AND latitude <= (@lat + @dt) AND longitude >= (@lon - @dt) AND longitude <= (@lon + @dt);
	END IF;
	SELECT c.*
	FROM City c
	JOIN GeoPatch p
		ON (c.id = p.id)
	WHERE (ccode IS NULL) OR (country_code = ccode)
	ORDER BY geo_dist(@lat, @lon, latitude, longitude) ASC
	LIMIT k;
END;
