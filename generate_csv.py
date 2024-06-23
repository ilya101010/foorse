import pandas as pd
import sqlite3
import re
conn = sqlite3.connect("dbs/vpo1/vpo1_2023.db")

table_titles = {x[0]: x[1] for x in pd.read_sql("SELECT table_std_id, tags.tag_name FROM table_std INNER JOIN tags ON table_std.table_title_tag_id = tags.tag_id", conn).values.tolist()}

def extract_number(col_name):
    match = re.search(r'\b(\d+)$', col_name)
    return int(match.group(1)) if match else float('inf')

for table_std_id, title in table_titles.items():
    filename = title.split(" ")[0].replace('.', '_') + '.tsv'
    print(title)
    tbl = pd.read_sql_query(f"""SELECT region, taglist as tags, data.indicator_id, indicator_name as indicator, data.subindicator_id as subindicator, value FROM data
	INNER JOIN tables ON tables.table_id = data.table_id
	INNER JOIN taglists ON tables.table_id = taglists.table_id
	INNER JOIN regions ON tables.table_id = regions.table_id
	INNER JOIN indicators on data.indicator_id = indicators.indicator_id
	INNER JOIN subindicators on data.subindicator_id = subindicators.subindicator_id
	WHERE tables.table_std_id = {table_std_id}
    ORDER BY subindicators.subindicator_id
    """, conn)
    tbl['value'] = pd.to_numeric(tbl['value'], errors='coerce')

    indicator_count = pd.read_sql(f"""SELECT indicator_count FROM table_std WHERE table_std_id = {table_std_id}""", conn)["indicator_count"][0]
    subindicators = pd.read_sql(f"""SELECT subindicator_id, subindicator_name FROM subindicators WHERE table_std_id = {table_std_id} ORDER BY subindicators.subindicator_id""", conn)
    subindicator_dict = subindicators.set_index('subindicator_id').to_dict()['subindicator_name']
    IC_names = subindicators['subindicator_name'].to_list()[:indicator_count]
    # IC_names = pd.read_sql(f"""SELECT subindicator_name FROM subindicators WHERE table_std_id = {table_std_id} LIMIT {indicator_count} ORDER BY subindicators.subindicator_id""", conn)['subindicator_name'].to_list()

    # Split the 'indicator' column by " / "
    split_columns = tbl['indicator'].str.split(' / ', expand=True)

    # Insert the new columns in place of the original 'indicator' column
    indicator_index = tbl.columns.get_loc('indicator')
    for i, col_name in enumerate(IC_names):
        tbl.insert(indicator_index + i, col_name, split_columns[i])

    # Drop the original 'indicator' column
    tbl.drop(columns=['indicator'], inplace=True)
    id_columns = ["region", "tags"] + IC_names
    pivotted = tbl.pivot_table(values = "value", index = ["region", "tags"] + IC_names, columns = ["subindicator"]).reset_index(drop = True)
    subindicator_columns = sorted(pivotted.columns[len(id_columns):])
    new_column_order = id_columns + subindicator_columns
    pivotted[new_column_order].rename(columns = subindicator_dict).to_csv('tsv/vpo1/2023/'+filename, sep='\t')

conn.close()