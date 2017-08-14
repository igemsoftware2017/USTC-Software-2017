"""
This module aliases 'pymysql' to 'MySQLdb', since django only uses 'MySQLdb'
for database connection.
"""

import sys
import pymysql

sys.modules['MySQLdb'] = pymysql
