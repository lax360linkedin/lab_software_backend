import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import init_db, get_database

init_db()
db = get_database()
db.users.update_one({'email': 'reception@abc.com'}, {'$set': {'role': 'receptionist'}})
user = db.users.find_one({'email': 'reception@abc.com'}, {'_id': 0, 'email': 1, 'role': 1, 'name': 1})
print('Updated User in MongoDB:', user)
