#!/usr/bin/env python3
"""
数据库迁移脚本：添加avatar字段到users表
运行方式：python add_avatar_column.py
"""
import sqlite3
import os

def add_avatar_column():
    db_path = os.path.join(os.path.dirname(__file__), "smart_agriculture.db")
    
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查avatar列是否已存在
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'avatar' in columns:
            print("avatar列已存在，无需添加")
            conn.close()
            return True
        
        # 添加avatar列
        cursor.execute("ALTER TABLE users ADD COLUMN avatar VARCHAR(255)")
        
        conn.commit()
        conn.close()
        
        print("成功添加avatar列到users表")
        return True
        
    except Exception as e:
        print(f"添加avatar列失败: {e}")
        return False

if __name__ == "__main__":
    success = add_avatar_column()
    if success:
        print("数据库迁移完成")
    else:
        print("数据库迁移失败")
        exit(1)