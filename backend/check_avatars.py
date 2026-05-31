import sqlite3

conn = sqlite3.connect('smart_agriculture.db')
cursor = conn.cursor()
cursor.execute('SELECT id, username, avatar FROM users')
print('所有用户头像状态:')
for row in cursor.fetchall():
    print(row)
conn.close()