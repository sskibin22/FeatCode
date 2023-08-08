# FeatCode Implementation :: Testing
# author: Scott Skibin

from featcode import *

fc = FeatCode()
fc.open_db_connection()
# print(fc.get_all_seen_problems())
# print(fc.get_all_unseen_problems())
# fc.add_problem('https://leetcode.com/problems/binary-tree-upside-down/')
# fc.get_random_problem()
# fc.add_col('USOL')
# fc.get_random_problem()
# fc.add_col('TIME')
# print(fc.get_all_problem_ids())

# fc.add_problem('https://leetcode.com/problems/strong-password-checker/')
# fc.get_problem_by_title('Strong Password Checker')
# fc.remove_problem('Strong Password Checker')
fc.close_db_connection()