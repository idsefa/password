import sys
import random
import string
from datetime import datetime
import sqlite3
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QCheckBox, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox
from PyQt5.QtGui import QClipboard

class PasswordGeneratorApp(QWidget):
    def __init__(self):
        super().__init__()

        # 初始化UI和数据库
        self.init_ui()
        self.init_database()

    def init_ui(self):
        # UI元素
        self.site_label = QLabel("网站或应用程序名称:")
        self.site_input = QLineEdit()

        self.username_label = QLabel("用户名:")
        self.username_input = QLineEdit()

        self.uppercase_checkbox = QCheckBox("包含大写字母")
        self.special_chars_checkbox = QCheckBox("包含特殊字符")

        self.generate_button = QPushButton("生成密码")
        self.copy_button = QPushButton("复制密码")
        self.generated_password_label = QLabel("生成的密码:")

        # 布局
        layout = QVBoxLayout()
        layout.addWidget(self.site_label)
        layout.addWidget(self.site_input)
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.uppercase_checkbox)
        layout.addWidget(self.special_chars_checkbox)
        layout.addWidget(self.generate_button)
        layout.addWidget(self.copy_button)
        layout.addWidget(self.generated_password_label)

        self.setLayout(layout)

        # 信号与槽连接
        self.generate_button.clicked.connect(self.generate_password)
        self.copy_button.clicked.connect(self.copy_password_to_clipboard)

        # 设置窗口属性
        self.setWindowTitle("密码生成器")
        self.setGeometry(100, 100, 400, 300)

    def init_database(self):
        # 连接到SQLite数据库
        self.conn = sqlite3.connect('passwords.db')
        self.cursor = self.conn.cursor()

        # 创建密码表（如果不存在）
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS passwords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                site_name TEXT NOT NULL,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                timestamp INTEGER NOT NULL
            )
        ''')
        self.conn.commit()

    def generate_password(self):
        # 获取用户输入
        site_name = self.site_input.text()
        username = self.username_input.text()
        include_uppercase = self.uppercase_checkbox.isChecked()
        include_special_chars = self.special_chars_checkbox.isChecked()

        # 使用密码生成函数
        generated_password = self.generate_password_logic(site_name, username, include_uppercase, include_special_chars)

        # 显示生成的密码
        self.generated_password_label.setText(f"生成的密码: {generated_password}")

    def generate_password_logic(self, site_name, username, include_uppercase, include_special_chars):
        # 使用网站或应用程序名称和用户名作为种子
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
        self.cursor.execute('''
            INSERT INTO passwords (site_name, username, password, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (site_name, username, password, timestamp))
        self.conn.commit()

        return password

    def copy_password_to_clipboard(self):
        clipboard = QApplication.clipboard()
        password_to_copy = self.generated_password_label.text().split(":")[1].strip()
        clipboard.setText(password_to_copy)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PasswordGeneratorApp()
    window.show()
    sys.exit(app.exec_())
