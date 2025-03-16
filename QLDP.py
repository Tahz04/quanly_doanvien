import sys
import mysql.connector
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem
from datetime import datetime  # Thêm thư viện datetime để lấy ngày hôm nay


class QLDPApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("QLDP.ui", self)

        # Kết nối cơ sở dữ liệu và khởi tạo cursor
        self.conn = self.connect_db()
        if self.conn:
            self.cursor = self.conn.cursor()
        else:
            self.cursor = None

        self.load_data()
        self.cbbTrangThai.currentIndexChanged.connect(self.filter_data)
        self.btnThongKe.clicked.connect(self.show_statistics)
        self.btnThuPhi.clicked.connect(self.open_thu_phi_dialog)
        self.btnUpdateNgayNop.clicked.connect(self.update_ngay_nop)  # Kết nối sự kiện cho nút cập nhật ngày nộp

    def connect_db(self):
        """Kết nối MySQL"""
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="doanvien_db"
            )
            return conn
        except mysql.connector.Error as e:
            print("Lỗi kết nối MySQL:", e)
            return None

    def load_data(self, filter_status="Tất cả"):
        """Tải dữ liệu từ cơ sở dữ liệu và hiển thị lên bảng"""
        if not self.conn:
            return

        query = "SELECT maDP, (SELECT hoTen FROM doanvien WHERE doanvien.maDV = doanphi.maDV) AS hoTen, soTien, ngayNop, ghiChu, trangThai FROM doanphi"
        if filter_status == "Đã nộp" or filter_status == "Chưa nộp":
            query += " WHERE trangThai = %s"
            self.cursor.execute(query, (filter_status,))
        else:
            self.cursor.execute(query)

        rows = self.cursor.fetchall()
        self.tableView_DoanPhi.setRowCount(len(rows))
        for row_idx, row_data in enumerate(rows):
            for col_idx, value in enumerate(row_data):
                self.tableView_DoanPhi.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

    def filter_data(self):
        """Lọc dữ liệu theo trạng thái được chọn"""
        selected_status = self.cbbTrangThai.currentText()
        self.load_data(selected_status)

    def show_statistics(self):
        """Hiển thị thống kê về tình hình thu phí"""
        if not self.conn:
            return

        self.cursor.execute("SELECT SUM(soTien) FROM doanphi WHERE trangThai='Đã nộp'")
        total_collected = self.cursor.fetchone()[0] or 0

        self.cursor.execute("SELECT COUNT(*) FROM doanphi WHERE trangThai='Chưa nộp'")
        not_paid_count = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COUNT(*) FROM doanphi WHERE trangThai='Đã nộp'")
        paid_count = self.cursor.fetchone()[0]

        QMessageBox.information(self, "Thống kê",
                                f"Tổng thu: {total_collected} VND\nĐã nộp: {paid_count}\nChưa nộp: {not_paid_count}")

    def open_thu_phi_dialog(self):
        """Mở hộp thoại thu phí"""
        dialog = ThuPhiDialog(self)
        dialog.exec_()
        self.load_data()

    def update_ngay_nop(self):
        """Cập nhật ngày nộp thành ngày hôm nay cho các đoàn viên đã chọn"""
        if not self.conn:
            return

        selected_indexes = self.tableView_DoanPhi.selectionModel().selectedIndexes()
        if not selected_indexes:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn ít nhất một đoàn viên để cập nhật ngày nộp!")
            return

        # Lấy danh sách các hàng được chọn (tránh trùng lặp)
        selected_rows = set(index.row() for index in selected_indexes)

        # Lấy ngày hôm nay
        today = datetime.now().strftime("%Y-%m-%d")

        try:
            for row in selected_rows:
                maDP = self.tableView_DoanPhi.item(row, 0).text()  # Lấy mã đoàn phí từ cột đầu tiên
                query = "UPDATE doanphi SET ngayNop = %s WHERE maDP = %s"
                self.cursor.execute(query, (today, maDP))
                self.conn.commit()

            QMessageBox.information(self, "Thông báo", "Cập nhật ngày nộp thành công!")
            self.load_data()  # Tải lại dữ liệu để cập nhật bảng
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Lỗi CSDL", f"Lỗi MySQL: {err}")

    def closeEvent(self, event):
        """Đóng kết nối cơ sở dữ liệu khi đóng ứng dụng"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        event.accept()


class ThuPhiDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("ThuPhiDialog.ui", self)

        self.btnLuu.clicked.connect(self.save_payment)
        self.btnHuy.clicked.connect(self.close)

    def save_payment(self):
        """Lưu thông tin thu phí vào cơ sở dữ liệu"""
        doan_vien_input = self.txtDoanVien.text().strip()
        so_tien = self.txtSoTien.text().strip()
        ngay_nop = self.dateNgayNop.date().toString("yyyy-MM-dd")
        ghi_chu = self.txtGhiChu.text().strip()

        if not doan_vien_input or not so_tien:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập đầy đủ thông tin!")
            return

        try:
            so_tien = float(so_tien)
        except ValueError:
            QMessageBox.warning(self, "Lỗi", "Số tiền không hợp lệ!")
            return

        if ngay_nop == "2000-01-01":
            ngay_nop = None

        try:
            # Sử dụng kết nối từ parent (QLDPApp)
            parent = self.parent()
            if not parent.conn:
                QMessageBox.warning(self, "Lỗi", "Không thể kết nối cơ sở dữ liệu!")
                return

            cursor = parent.conn.cursor()

            cursor.execute("SELECT maDV FROM doanvien WHERE maDV = %s OR hoTen = %s",
                           (doan_vien_input, doan_vien_input))
            result = cursor.fetchone()

            if not result:
                QMessageBox.warning(self, "Lỗi", "Không tìm thấy đoàn viên!")
                return

            ma_dv = result[0]

            query = "INSERT INTO doanphi (maDV, soTien, ngayNop, ghiChu) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (ma_dv, so_tien, ngay_nop, ghi_chu))
            parent.conn.commit()

            QMessageBox.information(self, "Thông báo", "Thu phí thành công!")
            self.close()
            parent.load_data()

        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Lỗi CSDL", f"Lỗi MySQL: {err}")

        finally:
            if cursor:
                cursor.close()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = QLDPApp()
    window.show()
    sys.exit(app.exec_())