from featcode import *

fc = FeatCode()
fc.open_db_connection()
# print(fc.get_all_seen_problems())
# print(fc.get_all_unseen_problems())
# fc.add_problem('https://leetcode.com/problems/binary-tree-upside-down/')
# fc.get_random_problem()
# fc.add_col('USOL')
fc.get_random_problem()
fc.close_db_connection()