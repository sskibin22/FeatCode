from featcode import *

fc = FeatCode()
fc.open_db_connection()
print(fc.get_all_seen_problems())
print(fc.get_all_unseen_problems())
fc.close_db_connection()