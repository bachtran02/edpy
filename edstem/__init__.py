import sys
import logging

# config logger
log = logging.getLogger(__name__)

fmt = logging.Formatter(
    '[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S')

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(fmt)
log.addHandler(handler)
log.setLevel(logging.DEBUG)