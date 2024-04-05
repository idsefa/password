import sys
import random
import string
from datetime import datetime
import sqlite3
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QCheckBox, QPushButton, QVBoxLayout, \
    QHBoxLayout, QMessageBox, QTableWidget, QTableWidgetItem, QDialog, QFormLayout, QDialogButtonBox, QInputDialog
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator

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
        self.show_history_button = QPushButton("查阅历史密码")
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
        layout.addWidget(self.show_history_button)
        layout.addWidget(self.generated_password_label)

        self.setLayout(layout)

        # 信号与槽连接
        self.generate_button.clicked.connect(self.generate_password)
        self.copy_button.clicked.connect(self.copy_password_to_clipboard)
        self.show_history_button.clicked.connect(self.show_password_history)

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

    def show_password_history(self):
        history_window = PasswordHistoryWindow(self)
        history_window.exec_()

class PasswordHistoryWindow(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("密码历史记录")
        self.setGeometry(200, 200, 500, 300)

        # 数据库连接
        self.conn = sqlite3.connect('passwords.db')
        self.cursor = self.conn.cursor()

        # 获取密码历史记录
        self.password_history = self.get_password_history()

        # 创建表格
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "网站名称", "用户名", "密码", "时间戳"])

        # 填充表格
        self.populate_table()

        # 按钮布局
        button_layout = QHBoxLayout()
        edit_button = QPushButton("编辑密码")
        edit_button.clicked.connect(self.edit_password)
        delete_button = QPushButton("删除密码")
        delete_button.clicked.connect(self.delete_password)
        edit_site_button = QPushButton("编辑网站信息")
        edit_site_button.clicked.connect(self.edit_site_info)
        edit_username_button = QPushButton("编辑用户名")
        edit_username_button.clicked.connect(self.edit_username)
        button_layout.addWidget(edit_button)
        button_layout.addWidget(delete_button)
        button_layout.addWidget(edit_site_button)
        button_layout.addWidget(edit_username_button)

        # 搜索布局
        search_layout = self.setup_search_ui()

        # 主布局
        main_layout = QVBoxLayout()
        main_layout.addLayout(search_layout)  # 将搜索布局添加到主布局
        main_layout.addWidget(self.table)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    def setup_search_ui(self):
        # 搜索框
        self.search_label = QLabel("搜索关键字:")
        self.search_input = QLineEdit()
        self.search_input.setValidator(QRegExpValidator(QRegExp("[a-zA-Z0-9_]+"), self))
        self.search_button = QPushButton("搜索")
        self.search_button.clicked.connect(self.search_passwords)

        # 布局
        search_layout = QHBoxLayout()
        search_layout.addWidget(self.search_label)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)

        return search_layout

    def search_passwords(self):
        keyword = self.search_input.text().strip()
        if keyword:
            keyword = f'%{keyword}%'

            # 使用 LIKE 进行模糊搜索
            self.cursor.execute('''
                SELECT * FROM passwords
                WHERE site_name LIKE ? OR username LIKE ? OR password LIKE ?
            ''', (keyword, keyword, keyword))
            self.password_history = self.cursor.fetchall()

            # 刷新表格
            self.populate_table()
        else:
            QMessageBox.warning(self, '警告', '请输入搜索关键字！')

    def get_password_history(self):
        self.cursor.execute("SELECT * FROM passwords")
        return self.cursor.fetchall()

    def populate_table(self):
        self.table.setRowCount(len(self.password_history))
        for row_num, row_data in enumerate(self.password_history):
            for col_num, col_data in enumerate(row_data):
                item = QTableWidgetItem(str(col_data))
                self.table.setItem(row_num, col_num, item)

    def edit_password(self):
        selected_row = self.table.currentRow()
        if selected_row != -1:
            password_id = int(self.table.item(selected_row, 0).text())
            password = self.table.item(selected_row, 3).text()

            # 提示用户输入新密码
            new_password, ok = QInputDialog.getText(self, "编辑密码", "请输入新密码:", QLineEdit.Password)

            if ok:
                # 更新数据库中的密码
                self.cursor.execute('''
                    UPDATE passwords
                    SET password = ?
                    WHERE id = ?
                ''', (new_password, password_id))
                self.conn.commit()

                # 刷新表格
                self.password_history = self.get_password_history()
                self.populate_table()

    def delete_password(self):
        selected_row = self.table.currentRow()
        if selected_row != -1:
            password_id = int(self.table.item(selected_row, 0).text())

            # 提示用户确认删除
            confirm_dialog = QMessageBox.question(self, '确认删除', '确定要删除该密码吗？',
                                                  QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if confirm_dialog == QMessageBox.Yes:
                # 从数据库中删除密码
                self.cursor.execute('''
                    DELETE FROM passwords
                    WHERE id = ?
                ''', (password_id,))
                self.conn.commit()

                # 刷新表格
                self.password_history = self.get_password_history()
                self.populate_table()

    def edit_site_info(self):
        selected_row = self.table.currentRow()
        if selected_row != -1:
            password_id = int(self.table.item(selected_row, 0).text())
            current_site_name = self.table.item(selected_row, 1).text()

            # 提示用户输入新的网站信息
            new_site_name, ok = QInputDialog.getText(self, "编辑网站信息", "请输入新的网站信息:", QLineEdit.Normal, current_site_name)

            if ok:
                # 更新数据库中的网站信息
                self.cursor.execute('''
                    UPDATE passwords
                    SET site_name = ?
                    WHERE id = ?
                ''', (new_site_name, password_id))
                self.conn.commit()

                # 刷新表格
                self.password_history = self.get_password_history()
                self.populate_table()

    def edit_username(self):
        selected_row = self.table.currentRow()
        if selected_row != -1:
            password_id = int(self.table.item(selected_row, 0).text())
            current_username = self.table.item(selected_row, 2).text()

            # 提示用户输入新的用户名
            new_username, ok = QInputDialog.getText(self, "编辑用户名", "请输入新的用户名:", QLineEdit.Normal, current_username)

            if ok:
                # 更新数据库中的用户名
                self.cursor.execute('''
                    UPDATE passwords
                    SET username = ?
                    WHERE id = ?
                ''', (new_username, password_id))
                self.conn.commit()

                # 刷新表格
                self.password_history = self.get_password_history()
                self.populate_table()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PasswordGeneratorApp()
    window.show()
    sys.exit(app.exec_())
