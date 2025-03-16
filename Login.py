import sys
import mysql.connector
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.uic import loadUi
from dashboard import DashboardWindow  # Import Dashboard từ dashboard.py


def connect_db():
    """Kết nối cơ sở dữ liệu MySQL"""
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="doanvien_db"
        )
        return conn
    except mysql.connector.Error as err:
        QMessageBox.critical(None, "Lỗi kết nối", f"Không thể kết nối MySQL: {err}")
        sys.exit()


class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("login.ui", self)  # Load giao diện từ file .ui

        # Kết nối sự kiện cho nút
        self.btnDangnhap.clicked.connect(self.login_user)
        self.btnDangky.clicked.connect(self.register_user)

    def login_user(self):
        """Xử lý đăng nhập"""
        username = self.txtUsername.text().strip()
        password = self.txtPassword.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập đầy đủ thông tin!")
            return

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            QMessageBox.information(self, "Thành công", "Đăng nhập thành công!")
            self.open_dashboard(username)  # ✅ Truyền `username` vào Dashboard
        else:
            QMessageBox.warning(self, "Lỗi", "Sai tên đăng nhập hoặc mật khẩu!")

    def open_dashboard(self, username):
        """Mở giao diện Dashboard sau khi đăng nhập thành công"""
        self.dashboard = DashboardWindow(username)  # ✅ Truyền `username` vào DashboardWindow
        self.dashboard.show()
        self.close()

    def register_user(self):
        """Xử lý đăng ký"""
        username = self.txtUsername.text().strip()
        password = self.txtPassword.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập đầy đủ thông tin!")
            return

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        conn.commit()
        conn.close()
        QMessageBox.information(self, "Thành công", "Đăng ký thành công!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())
