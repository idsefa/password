import random
import string
from datetime import datetime

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
