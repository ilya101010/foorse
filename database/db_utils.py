import sqlite3
import pandas as pd
import os
import math
import ai.ai_utils as ai
from forms.generic_parser import GenericParser
from logger import logger
import utils
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

def process_html_file(file_path, db_path, ref_file = False, ref = None, statform='-'):
	if not ref_file:
		refr = ref
	else:
		refr = {}

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
	 
		if ref_file:
			parser = GenericParser(df, generate_title_id = ai.ai_title_id,
				generate_indicator_count = ai.ai_indicator_count,
				reference = ref)
			logger.info(f'Parsed a table using GenericParser')
			logger.info(f'AI detected title: {parser.title}')
			logger.info(f'AI detected indicator_count: {parser.indicator_count}')
		else:
			parser = GenericParser(df, reference = ref)

		# reference file handling: adding new title tag, new table_std
		if ref_file and parser.title not in refr.keys():
			cursor.execute("SELECT tag_id FROM tags WHERE tag_name = ?", (parser.title, ))
			table_title_tag_id = cursor.fetchone()
			if not table_title_tag_id:
				cursor.execute('INSERT INTO tags (tag_name) VALUES (?)', [parser.title])
				table_title_tag_id = cursor.lastrowid
			else:
				table_title_tag_id = table_title_tag_id[0]
			cursor.execute('INSERT INTO table_std (table_title_tag_id, indicator_count, description) VALUES (?, ?, ?)', [table_title_tag_id, parser.indicator_count, parser.description])
			table_std_id = cursor.lastrowid
			refr[parser.title] = {"indicator_count": parser.indicator_count,
						 		  "description": parser.description,
								  'table_std_id': table_std_id,
								  'table_title_tag_id': table_title_tag_id}

		# table DB handling
		try:
			table_title = parser.title
			indicator_count = parser.indicator_count
			table_std_id = refr[table_title]['table_std_id']
			table_name = f"{os.path.basename(file_path)}_table_{table_index}"
			cursor.execute('INSERT INTO tables (table_name, table_filename, table_std_id) VALUES (?, ?, ?)', [table_name, str(file_path), table_std_id])
			table_id = cursor.lastrowid
		except BaseException as e:
			logger.error(traceback.format_exc())
			logger.error('Not our tags, moving to next table')
			continue

		# tag DB handling
		tag_ids = []
		for tag in parser.tags:
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

		# indicator DB handling
		indicator_ids = []
		for indicator in parser.indicators:
			indicator_name = ' / '.join(map(str, indicator))
			cursor.execute("SELECT indicator_id FROM indicators WHERE indicator_name = ? AND table_std_id = ?", (indicator_name, table_std_id, ))
			indicator_id = cursor.fetchone()
			if not indicator_id:
				cursor.execute("INSERT INTO indicators (indicator_name, table_std_id) VALUES (?, ?)", [indicator_name, table_std_id])
				indicator_id = cursor.lastrowid
			else:
				indicator_id = indicator_id[0]
			indicator_ids.append(indicator_id)

		# subindicator DB handling
		subindicator_ids = []
		for subindicator in parser.subindicators:
			subindicator_name = ' > '.join(map(str, subindicator))
			cursor.execute("SELECT subindicator_id FROM subindicators WHERE subindicator_name = ? AND table_std_id = ?", (subindicator_name, table_std_id, ))
			subindicator_id = cursor.fetchone()
			if not subindicator_id:
				cursor.execute("INSERT INTO subindicators (subindicator_name, table_std_id) VALUES (?, ?)", [subindicator_name, table_std_id])
				subindicator_id = cursor.lastrowid
			else:
				subindicator_id = subindicator_id[0]
			subindicator_ids.append(subindicator_id)

		# values DB handling
		data_values = []
		for i, row in enumerate(parser.raw_values):
			for j, value in enumerate(row):
				if isinstance(value, str) or not math.isnan(value):
					data_values.append((table_id, indicator_ids[i], subindicator_ids[j + parser.indicator_count], value))
		cursor.executemany("INSERT INTO data (table_id, indicator_id, subindicator_id, value) VALUES (?, ?, ?, ?)", data_values)

		conn.commit()
	conn.close()

	if ref_file:
		return refr
	
def process_excel_file(file_path, db_path, ref_file = False, ref = None, statform='-'):
	if not ref_file:
		refr = ref
	else:
		refr = {}

	if ref_file:
		logger.info(f'Entering ref_file {file_path}')
	conn = sqlite3.connect(db_path)
	cursor = conn.cursor()
	
	extension = os.path.splitext(file_path)[1][1:]
	if extension == 'xlsx':
		tables = utils.file_utils.read_xlsx_to_dataframe(file_path)
	elif extension == 'xls':
		tables = utils.file_utils.read_xls_to_dataframe(file_path)
	else:
		return

	pd.set_option('future.no_silent_downcasting', True)

	for table_index, df in tables:
		if ref_file:
			logger.info(f'Entering table #{table_index}')
		df = df.dropna(how='all')
		df = df.replace('', float('NaN')).dropna(axis=1, how='all').reset_index(drop=True)

		titular = df.map(lambda x: "ФЕДЕРАЛЬНОЕ СТАТИСТИЧЕСКОЕ НАБЛЮДЕНИЕ" in str(x)).any().any()
		if titular:
			logger.info('Ditched titular page')
			continue
	 
		if ref_file:
			parser = GenericParser(df, generate_title_id = ai.ai_title_id,
				generate_indicator_count = ai.ai_indicator_count,
				reference = ref)
			logger.info(f'Parsed a table using GenericParser')
			logger.info(f'AI detected title: {parser.title}')
			logger.info(f'AI detected indicator_count: {parser.indicator_count}')
		else:
			parser = GenericParser(df, reference = ref)

		# reference file handling: adding new title tag, new table_std
		if ref_file and parser.title not in refr.keys():
			cursor.execute("SELECT tag_id FROM tags WHERE tag_name = ?", (parser.title, ))
			table_title_tag_id = cursor.fetchone()
			if not table_title_tag_id:
				cursor.execute('INSERT INTO tags (tag_name) VALUES (?)', [parser.title])
				table_title_tag_id = cursor.lastrowid
			else:
				table_title_tag_id = table_title_tag_id[0]
			cursor.execute('INSERT INTO table_std (table_title_tag_id, indicator_count, description) VALUES (?, ?, ?)', [table_title_tag_id, parser.indicator_count, parser.description])
			table_std_id = cursor.lastrowid
			refr[parser.title] = {"indicator_count": parser.indicator_count,
						 		  "description": parser.description,
								  'table_std_id': table_std_id,
								  'table_title_tag_id': table_title_tag_id}

		# table DB handling
		try:
			table_title = parser.title
			indicator_count = parser.indicator_count
			table_std_id = refr[table_title]['table_std_id']
			table_name = f"{os.path.basename(file_path)}_table_{table_index}"
			cursor.execute('INSERT INTO tables (table_name, table_filename, table_std_id) VALUES (?, ?, ?)', [table_name, str(file_path), table_std_id])
			table_id = cursor.lastrowid
		except BaseException as e:
			logger.error(traceback.format_exc())
			logger.error('Not our tags, moving to next table')
			continue

		# tag DB handling
		tag_ids = []
		for tag in parser.tags:
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

		# indicator DB handling
		indicator_ids = []
		for indicator in parser.indicators:
			indicator_name = ' / '.join(map(str, indicator))
			cursor.execute("SELECT indicator_id FROM indicators WHERE indicator_name = ?", (indicator_name,))
			indicator_id = cursor.fetchone()
			if not indicator_id:
				cursor.execute("INSERT INTO indicators (indicator_name, table_std_id) VALUES (?, ?)", [indicator_name, table_std_id])
				indicator_id = cursor.lastrowid
			else:
				indicator_id = indicator_id[0]
			indicator_ids.append(indicator_id)

		# subindicator DB handling
		subindicator_ids = []
		for subindicator in parser.subindicators:
			subindicator_name = ' > '.join(map(str, subindicator))
			cursor.execute("SELECT subindicator_id FROM subindicators WHERE subindicator_name = ?", (subindicator_name,))
			subindicator_id = cursor.fetchone()
			if not subindicator_id:
				cursor.execute("INSERT INTO subindicators (subindicator_name, table_std_id) VALUES (?, ?)", [subindicator_name, table_std_id])
				subindicator_id = cursor.lastrowid
			else:
				subindicator_id = subindicator_id[0]
			subindicator_ids.append(subindicator_id)

		# values DB handling
		data_values = []
		for i, row in enumerate(parser.raw_values):
			for j, value in enumerate(row):
				if isinstance(value, str) or not math.isnan(value):
					data_values.append((table_id, indicator_ids[i], subindicator_ids[j + parser.indicator_count], value))
		cursor.executemany("INSERT INTO data (table_id, indicator_id, subindicator_id, value) VALUES (?, ?, ?, ?)", data_values)

		conn.commit()
	conn.close()

	if ref_file:
		return refr