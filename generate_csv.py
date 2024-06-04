import pandas as pd
import sqlite3
import re
conn = sqlite3.connect("spo1_2023_full.db")

table_titles = {x[0]: x[1] for x in pd.read_sql("SELECT table_std_id, tags.tag_name FROM table_std INNER JOIN tags ON table_std.table_title_tag_id = tags.tag_id", conn).values.tolist()}

def extract_number(col_name):
    match = re.search(r'\b(\d+)$', col_name)
    return int(match.group(1)) if match else float('inf')

for table_std_id, title in table_titles.items():
    filename = title.split(" ")[0].replace('.', '_') + '.tsv'
    print(title)
    tbl = pd.read_sql_query(f"""SELECT region, taglist as tags, indicator_name as indicator, subindicator_name as subindicator, value FROM data
	INNER JOIN tables ON tables.table_id = data.table_id
	INNER JOIN taglists ON tables.table_id = taglists.table_id
	INNER JOIN regions ON tables.table_id = regions.table_id
	INNER JOIN indicators on data.indicator_id = indicators.indicator_id
	INNER JOIN subindicators on data.subindicator_id = subindicators.subindicator_id
	WHERE tables.table_std_id = {table_std_id}""", conn)
    tbl['value'] = pd.to_numeric(tbl['value'], errors='coerce')
    tbl = tbl.dropna(subset=['value'])
    tbl = tbl.pivot_table(values = "value", index = ["region", "tags", "indicator"], columns = ["subindicator"])

    # Columns to exclude
    exclude_columns = {'region', 'tags', 'indicator'}

    # Separate columns into those to sort and those to exclude
    columns_to_sort = [col for col in tbl.columns if col not in exclude_columns]
    columns_excluded = [col for col in tbl.columns if col in exclude_columns]

    # Sort columns based on the extracted number
    sorted_columns = sorted(columns_to_sort, key=extract_number)

    # Combine excluded columns with sorted columns
    new_column_order = columns_excluded + sorted_columns

    # Rearrange DataFrame
    tbl = tbl[new_column_order]
    
    tbl.to_csv('tsv/spo1/2023/'+filename, sep='\t')

conn.close()