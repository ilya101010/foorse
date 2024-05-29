SELECT * FROM data
INNER JOIN tables ON tables.table_id = data.table_id
WHERE tables.table_std_id = 1;

SELECT table_id, group_concat(tag_name, "; ") FROM table_tags
LEFT JOIN tags ON table_tags.tag_id = tags.tag_id
WHERE tags.tag_type = "filter"
GROUP BY table_id;

SELECT * FROM data
INNER JOIN tables ON tables.table_id = data.table_id
INNER JOIN taglists ON tables.table_id = taglists.table_id
WHERE tables.table_std_id = 1
LIMIT 100;

CREATE TABLE taglists AS 
SELECT table_id, group_concat(tag_name, '; ') AS taglist FROM table_tags
	LEFT JOIN tags ON table_tags.tag_id = tags.tag_id
	WHERE tags.tag_type = 'filter'
	GROUP BY table_id;

SELECT region, taglist as tags, indicator_name as indicator, subindicator_name as subindicator, value FROM data
	INNER JOIN tables ON tables.table_id = data.table_id
	INNER JOIN taglists ON tables.table_id = taglists.table_id
	INNER JOIN regions ON tables.table_id = regions.table_id
	INNER JOIN indicators on data.indicator_id = indicators.indicator_id
	INNER JOIN subindicators on data.subindicator_id = subindicators.subindicator_id
	WHERE tables.table_std_id = 7;

CREATE TABLE regions AS
	SELECT table_id, tag_name AS region, tag_id FROM table_tags
	LEFT JOIN tags ON table_tags.tag_id = tags.tag_id
	WHERE tags.tag_type = 'region';