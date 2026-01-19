import logging
import sys


# Configures the global root logger format
# The StreamHandler class sends the logs to the console
# stdout is typically white (OS contingent)
# stderr is typically red (OS contingent) -> stream parameter default
logging.basicConfig(
    level=logging.DEBUG,
    handlers=[logging.StreamHandler(stream=sys.stdout)],
    format="%(asctime)s | %(levelname)s | %(name)s: Line %(lineno)d | %(message)s",
)

# TODO get fastAPI / route working -> returns text == "hello world"
