import sys
from fonduer import Meta, init_logging
import s1_1_create_db as cd
# Configure logging for Fonduer
# init_logging(log_dir="logs")

# ATTRIBUTE = sys.argv[1] if len(sys.argv[1]) > 0 else '3ray_demo_1'

def get_session():
    session = Meta.init(cd.conn_string).Session()
    return session

# print(cd.conn_string)
# session = Meta.init(cd.conn_string).Session()

# get_session(cd.conn_string)