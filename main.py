import config
from logger import logger
from database.db_utils import is_db_empty, run_schema_sql, process_html_file
from utils.file_utils import get_html_files, pick_reference_file
from rich.prompt import Prompt
from rich.console import Console
from rich.progress import track
import sqlite3
from pathlib import Path

def main():
    console = Console()
    statform = Prompt.ask('Enter full statistical form name in Russian', default=config.statform)
    directory = Prompt.ask('Enter directory for lookup', default=config.directory)
    html_files = get_html_files(directory)
    
    schema_sql = 'database/schema.sql'
    db_path = Prompt.ask('Enter preferred database file', default=config.db_path)

    conn = sqlite3.connect(db_path)
    if is_db_empty(conn):
        logger.info('Empty DB; I\'ll run schema file on it')
        try:
            run_schema_sql(conn, schema_sql)
        except BaseException as e:
            logger.error(f'I\'ve encountered an error: {str(e)}')
            logger.error('Please, fix schema issue. Finishing')
            return
        else:
            logger.info('Schema loaded successfully')
    conn.close()

    reference_file = pick_reference_file(html_files)
    html_files.remove(reference_file)
    ref_result = process_html_file(reference_file, db_path, ref_file=True, statform=statform)

    for file_path in track(html_files, description="Processing HTML files"):
        logger.info(f"Processing {file_path}")
        process_html_file(file_path, db_path, ref=ref_result)

    logger.info("All files processed.")

if __name__ == "__main__":
    main()