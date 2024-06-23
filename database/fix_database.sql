-- find 

SELECT subindicators.subindicator_name, subindicators.subindicator_id as new_subindicator_id, table_std.table_std_id as new_table_std_id, TT.subindicator_id as old_subindicator_id, TT.table_std_id as old_table_std_id FROM subindicators
    INNER JOIN table_std ON subindicators.table_std_id = table_std.table_std_id
    INNER JOIN tags on table_std.table_title_tag_id = tags.tag_id
    INNER JOIN (SELECT subindicator_id, subindicator_name, table_std.table_std_id, tag_name as table_std_name FROM subindicators
    INNER JOIN table_std ON subindicators.table_std_id = table_std.table_std_id
    INNER JOIN tags on table_std.table_title_tag_id = tags.tag_id
    WHERE table_std.table_std_id = 6) TT
    ON TT.subindicator_name = subindicators.subindicator_name
WHERE table_std.table_std_id = 5

-- update indicators in data with new ones

WITH X AS (
    SELECT 
        indicators.indicator_id AS new_indicator_id, 
        TT.indicator_id AS old_indicator_id
    FROM 
        indicators
    INNER JOIN 
        table_std ON indicators.table_std_id = table_std.table_std_id
    INNER JOIN 
        tags ON table_std.table_title_tag_id = tags.tag_id
    INNER JOIN (
        SELECT 
            indicator_id, 
            indicator_name, 
            table_std.table_std_id, 
            tag_name AS table_std_name 
        FROM 
            indicators
        INNER JOIN 
            table_std ON indicators.table_std_id = table_std.table_std_id
        INNER JOIN 
            tags ON table_std.table_title_tag_id = tags.tag_id
        WHERE 
            table_std.table_std_id = 6
    ) TT ON TT.indicator_name = indicators.indicator_name
    WHERE 
        table_std.table_std_id = 5
)
UPDATE 
    data
SET 
    indicator_id = X.new_indicator_id
FROM 
    X
WHERE 
    data.indicator_id = X.old_indicator_id;