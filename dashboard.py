import subprocess
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic

class DashboardWindow(QMainWindow):
    def __init__(self, username):
        super().__init__()
        uic.loadUi("dashboard.ui", self)  # Load giao diện

        # Hiển thị tên đăng nhập
        self.labeWelcome.setText(f"Chào mừng {username} đến với phần mềm quản lý đoàn viên")

        # Kết nối nút với sự kiện
        self.btnQLDV.clicked.connect(self.open_qldv)
        self.btnQLHD.clicked.connect(self.open_qlhd)
        self.btnQLDP.clicked.connect(self.open_qldp)
        self.btnBCTK.clicked.connect(self.open_bctk)


    def open_qldv(self):
        subprocess.Popen(["python", "QLDV.py"])

    def open_qlhd(self):
        subprocess.Popen(["python", "QLHD.py"])

    def open_qldp(self):
        subprocess.Popen(["python", "QLDP.py"])

    def open_bctk(self):
        subprocess.Popen(["python", "BCTK.py"])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DashboardWindow("Admin")  # Test với username "Admin"
    window.show()
    sys.exit(app.exec_())
