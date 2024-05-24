import sqlite3
import pandas as pd
import os
import math
from ai.ai_utils import ai_title_id, ai_indicator_count, ai_description
from logger import logger
import traceback

def is_db_empty(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    return len(tables) == 0

def run_schema_sql(conn, schema_sql_path):
    with open(schema_sql_path, 'r') as file:
        schema_sql = file.read()
    cursor = conn.cursor()
    cursor.executescript(schema_sql)
    conn.commit()

def process_html_file(file_path, db_path, ref_file=False, ref={}, statform='<пользователь не дал названия формы>'):
    def fix(lst):
        cleaned_list = [str(v) if isinstance(v, float) else v for v in lst]
        return [v for i, v in enumerate(cleaned_list) if i == 0 or v != cleaned_list[i - 1]]

    refr = ref
    if ref_file:
        logger.info(f'Entering ref_file {file_path}')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    tables = pd.read_html(file_path)

    for table_index, df in enumerate(tables):
        if ref_file:
            logger.info(f'Entering table #{table_index}')
        df = df.dropna(how='all')
        df = df.replace('', float('NaN')).dropna(axis=1, how='all').reset_index(drop=True)
        titular = df.map(lambda x: "ФЕДЕРАЛЬНОЕ СТАТИСТИЧЕСКОЕ НАБЛЮДЕНИЕ" in str(x)).any().any()
        if titular:
            logger.info('Ditched titular page')
            continue

        find_first = lambda search_string: next((index for index, row in df.iterrows() if row.astype(str).str.contains(search_string).any()), 10000)
        header_bottom = min(find_first("№ строки"), find_first("Наименование"))

        tag_ids = []
        for i in range(100):
            if isinstance(df.iloc[0, i], str):
                table_tags = list(df.iloc[0:header_bottom, i])
                break

        subindicator_bottom = next((i for i, value in enumerate(df.iloc[:, 0]) if value == '1'), 0)
        subindicators_df = df.iloc[header_bottom:subindicator_bottom+1]
        subindicators_df = subindicators_df.replace('', float('NaN')).dropna(axis=1, how='all')
        subindicators_fixed = [fix(subindicators_df[col].tolist()) for col in subindicators_df.columns]
        parsed_data = df.iloc[subindicator_bottom+1:, :].reset_index(drop=True)
        subindicator_names = list(map(lambda x: ' > '.join((map(str, x))), subindicators_fixed))

        if ref_file:
            title_id = ai_title_id(table_tags)
            table_title = table_tags[title_id]
            logger.info(f'[AI] Table title found: \'{table_title}\'')
            indicator_count = ai_indicator_count(table_title, subindicator_names)
            indicator_tmp = df.iloc[subindicator_bottom+1:,0:indicator_count].values.tolist()
            if indicator_count >= len(subindicator_names):
                logger.info(f'[AI] Indicator subindicators: {subindicator_names[0:indicator_count]} [-]')
            else:
                logger.info(f'[AI] Indicator subindicators: {subindicator_names[0:indicator_count]} [{subindicator_names[indicator_count]}]')
            description = ai_description(table_title, subindicator_names, statform, list(map(lambda x: ' / '.join(map(str, x)), indicator_tmp)))
            logger.info(f'[AI] Description generated: {description}')

            cursor.execute("SELECT tag_id FROM tags WHERE tag_name = ?", (table_title, ))
            table_title_tag_id = cursor.fetchone()
            if not table_title_tag_id:
                cursor.execute('INSERT INTO tags (tag_name) VALUES (?)', [table_title])
                table_title_tag_id = cursor.lastrowid
            else:
                table_title_tag_id = table_title_tag_id[0]

            cursor.execute('INSERT INTO table_std (table_title_tag_id, indicator_count, description) VALUES (?, ?, ?)', [table_title_tag_id, indicator_count, description])
            table_std_id = cursor.lastrowid

            refr[table_title] = {"indicator_count": indicator_count, "description": description, "table_std_id": table_std_id}

        try:
            # print(f"T1 {ref.keys()}")
            # print(f"T2 {table_tags}")
            table_title = list(set(ref.keys()) & set(table_tags))[0]
            indicator_count = refr[table_title]['indicator_count']
            table_std_id = refr[table_title]['table_std_id']
            table_name = f"{os.path.basename(file_path)}_table_{table_index}"
            cursor.execute('INSERT INTO tables (table_name, table_filename, table_std_id) VALUES (?, ?, ?)', [table_name, str(file_path), table_std_id])
            table_id = cursor.lastrowid
        except BaseException as e:
            logger.error(traceback.format_exc())
            logger.error('Not our tags, moving to next table')
            continue

        for tag in table_tags:
            if not isinstance(tag, str):
                continue
            cursor.execute("SELECT tag_id FROM tags WHERE tag_name = ?", (tag,))
            tag_id = cursor.fetchone()
            if not tag_id:
                cursor.execute('INSERT INTO tags (tag_name) VALUES (?)', [tag])
                tag_id = cursor.lastrowid
            else:
                tag_id = tag_id[0]
            tag_ids.append((table_id, tag_id))

        cursor.executemany("INSERT INTO table_tags (table_id, tag_id) VALUES (?, ?)", tag_ids)

        indicators = df.iloc[subindicator_bottom+1:,0:indicator_count].values.tolist()
        indicator_ids = []
        for indicator in indicators:
            indicator_name = ' / '.join(map(str, indicator))
            cursor.execute("SELECT indicator_id FROM indicators WHERE indicator_name = ?", (indicator_name,))
            indicator_id = cursor.fetchone()
            if not indicator_id:
                cursor.execute("INSERT INTO indicators (indicator_name) VALUES (?)", [indicator_name])
                indicator_id = cursor.lastrowid
            else:
                indicator_id = indicator_id[0]
            indicator_ids.append(indicator_id)

        subindicator_ids = []
        for subindicator_name in subindicator_names:
            cursor.execute("SELECT subindicator_id FROM subindicators WHERE subindicator_name = ?", (subindicator_name,))
            subindicator_id = cursor.fetchone()
            if not subindicator_id:
                cursor.execute("INSERT INTO subindicators (subindicator_name) VALUES (?)", [subindicator_name])
                subindicator_id = cursor.lastrowid
            else:
                subindicator_id = subindicator_id[0]
            subindicator_ids.append(subindicator_id)

        data_values = []
        for i, row in parsed_data.iloc[:,2:len(subindicator_ids)].iterrows():
            for j, value in enumerate(row):
                if isinstance(value, str) or not math.isnan(value):
                    data_values.append((table_id, indicator_ids[i], subindicator_ids[j], value))
        cursor.executemany("INSERT INTO data (table_id, indicator_id, subindicator_id, value) VALUES (?, ?, ?, ?)", data_values)
        conn.commit()
    conn.close()

    if ref_file:
        return refr