import random
import string
from datetime import datetime
import sqlite3

# 连接到SQLite数据库（如果不存在，则会创建一个新的数据库文件）
conn = sqlite3.connect('passwords.db')
cursor = conn.cursor()

# 创建密码表（如果不存在）
cursor.execute('''
    CREATE TABLE IF NOT EXISTS passwords (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        site_name TEXT NOT NULL,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        timestamp INTEGER NOT NULL
    )
''')
conn.commit()

def generate_password(site_name, username, include_uppercase=True, include_special_chars=True):
    # 使用网站或应用程序名称和用户名作为种子，以确保对于相同的站点名称和用户名生成的密码相同
    seed_string = site_name + username
    random.seed(seed_string)

    # 生成基本密码
    password = ''.join(random.choices(string.ascii_lowercase, k=8))

    # 根据参数决定是否包含大写字母
    if include_uppercase:
        password += random.choice(string.ascii_uppercase)

    # 根据参数决定是否包含特殊字符
    if include_special_chars:
        password += random.choice(string.punctuation)

    # 获取当前时间戳并添加到密码中
    timestamp = int(datetime.timestamp(datetime.now()))
    password += str(timestamp)

    # 将密码随机化
    password_list = list(password)
    random.shuffle(password_list)
    password = ''.join(password_list)

    # 将密码信息插入数据库
    cursor.execute('''
        INSERT INTO passwords (site_name, username, password, timestamp)
        VALUES (?, ?, ?, ?)
    ''', (site_name, username, password, timestamp))
    conn.commit()

    return password

# 获取用户输入
site_name = input("请输入网站或应用程序的名称：")
username = input("请输入用户名：")
include_uppercase = input("是否包含大写字母？ (y/n): ").lower() == 'y'
include_special_chars = input("是否包含特殊字符？ (y/n): ").lower() == 'y'

# 生成密码
generated_password = generate_password(site_name, username, include_uppercase, include_special_chars)

# 打印生成的密码
print(f"生成的密码为：{generated_password}")

# 关闭数据库连接
conn.close()
