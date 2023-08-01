from featcode import *

fc = FeatCode()
fc.open_db_connection()
fc.get_random_problem()
fc.close_db_connection()