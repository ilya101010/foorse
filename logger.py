import logging
from rich.logging import RichHandler

logger = logging.getLogger('my_logger')
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler('app.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

console_handler = RichHandler()

logger.addHandler(file_handler)
logger.addHandler(console_handler)