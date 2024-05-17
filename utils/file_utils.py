from pathlib import Path
import os

def get_html_files(directory):
    return list(Path(directory).rglob("*.html"))

def pick_reference_file(html_files):
    return max(html_files, key=os.path.getsize)