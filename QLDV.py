import sys
import mysql.connector
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QMessageBox, QWidget
from PyQt5.uic import loadUi
from PyQt5.QtCore import QDate

class AddDVForm(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi("AddDV.ui", self)

class QLDV(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("QLDV.ui", self)

        # Kết nối cơ sở dữ liệu và khởi tạo cursor
        self.conn = self.connect_db()
        if self.conn:
            self.cursor = self.conn.cursor()
        else:
            self.cursor = None

        self.load_data()  # Hiển thị danh sách đoàn viên
        self.load_combobox1()  # Load danh sách vào cbbLoc1
        self.load_combobox2()  # Load danh sách vào cbbLoc2

        # Bắt sự kiện
        self.btnTimKiem.clicked.connect(self.search_member)
        self.cbbLoc1.currentIndexChanged.connect(self.load_combobox2)  # Cập nhật danh sách cbbLoc2 khi thay đổi cbbLoc1
        self.cbbLoc2.currentIndexChanged.connect(self.filter_data)  # Lọc danh sách khi thay đổi cbbLoc2
        self.tableWidget.itemSelectionChanged.connect(self.on_table_item_selection)
        self.btnXoa.clicked.connect(self.delete_member)  # Thêm sự kiện xóa đoàn viên
        self.btnThem.clicked.connect(self.add_member)  # Thêm sự kiện thêm đoàn viên
        self.btnSua.clicked.connect(self.edit_member)  # Thêm sự kiện sửa đoàn viên
        self.on_table_item_selection()  # Đảm bảo nút được disable khi mở giao diện

    def connect_db(self):
        """Kết nối MySQL"""
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",  # Thay bằng mật khẩu MySQL của bạn
                database="doanvien_db"
            )
            return conn
        except mysql.connector.Error as e:
            print("Lỗi kết nối MySQL:", e)
            return None

    def load_data(self):
        """Hiển thị danh sách đoàn viên trong tableWidget."""
        if not self.conn:
            return

        self.cursor.execute(
            "SELECT maDV, hoTen, ngaySinh, gioiTinh, chiDoan, khoa, khoaHoc, chucVu, sdt, diaChi FROM doanvien")
        rows = self.cursor.fetchall()

        self.tableWidget.setRowCount(len(rows))
        self.tableWidget.setColumnCount(10)
        self.tableWidget.setHorizontalHeaderLabels(
            ["Mã", "Họ Tên", "Ngày Sinh", "Giới Tính", "Chi Đoàn", "Khoa", "Khóa Học", "Chức Vụ", "SĐT", "Địa chỉ"])

        for row_idx, row_data in enumerate(rows):
            for col_idx, col_data in enumerate(row_data):
                self.tableWidget.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))

    def search_member(self):
        """Tìm kiếm đoàn viên theo mã hoặc tên."""
        if not self.conn:
            return

        keyword = self.lineEdit.text().strip()
        if not keyword:
            self.load_data()
            return

        query = "SELECT maDV, hoTen, ngaySinh, gioiTinh, chiDoan, khoa, khoaHoc, chucVu, sdt, diaChi FROM doanvien WHERE maDV LIKE %s OR hoTen LIKE %s"
        self.cursor.execute(query, ('%' + keyword + '%', '%' + keyword + '%'))
        rows = self.cursor.fetchall()

        self.tableWidget.setRowCount(len(rows))
        for row_idx, row_data in enumerate(rows):
            for col_idx, col_data in enumerate(row_data):
                self.tableWidget.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))

    def load_combobox1(self):
        """Cập nhật danh sách trong cbbLoc1."""
        self.cbbLoc1.clear()
        self.cbbLoc1.addItems(["Tất cả", "Chi đoàn", "Khoa", "Khóa học"])  # Thêm mục 'Tất cả'

    def load_combobox2(self):
        """Cập nhật danh sách trong cbbLoc2 theo loại lọc đã chọn."""
        if not self.conn:
            return

        filter_option = self.cbbLoc1.currentText()

        # Nếu chọn "Tất cả", hiển thị toàn bộ danh sách
        if filter_option == "Tất cả":
            self.cbbLoc2.clear()
            self.cbbLoc2.addItem("Tất cả")
            self.load_data()
            return

        # Xác định cột tương ứng trong CSDL
        column_mapping = {
            "Chi đoàn": "chiDoan",
            "Khoa": "khoa",
            "Khóa học": "khoaHoc"
        }

        column_name = column_mapping.get(filter_option)
        if not column_name:
            return

        # Lấy danh sách giá trị duy nhất từ cột tương ứng
        query = f"SELECT DISTINCT {column_name} FROM doanvien ORDER BY {column_name}"
        self.cursor.execute(query)
        values = [row[0] for row in self.cursor.fetchall()]

        # Cập nhật combobox cbbLoc2
        self.cbbLoc2.clear()
        self.cbbLoc2.addItem("Tất cả")  # Giá trị mặc định
        self.cbbLoc2.addItems(values)

    def filter_data(self):
        """Lọc danh sách đoàn viên theo cbbLoc1 và cbbLoc2."""
        if not self.conn:
            return

        filter_option = self.cbbLoc1.currentText()
        selected_value = self.cbbLoc2.currentText()

        if filter_option == "Tất cả" or selected_value == "Tất cả":
            self.load_data()  # Hiển thị lại toàn bộ danh sách
            return

        # Xác định cột trong CSDL
        column_mapping = {
            "Chi đoàn": "chiDoan",
            "Khoa": "khoa",
            "Khóa học": "khoaHoc"
        }
        column_name = column_mapping.get(filter_option)
        if not column_name:
            return

        query = f"SELECT maDV, hoTen, ngaySinh, gioiTinh, chiDoan, khoa, khoaHoc, chucVu, sdt, diaChi FROM doanvien WHERE {column_name} = %s"
        self.cursor.execute(query, (selected_value,))
        rows = self.cursor.fetchall()

        self.tableWidget.setRowCount(len(rows))
        for row_idx, row_data in enumerate(rows):
            for col_idx, col_data in enumerate(row_data):
                self.tableWidget.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))

    def on_table_item_selection(self):
        has_selection = len(self.tableWidget.selectedItems()) > 0
        self.btnSua.setEnabled(has_selection)
        self.btnXoa.setEnabled(has_selection)

    def delete_member(self):
        """Xóa đoàn viên được chọn."""
        if not self.conn:
            return

        selected_row = self.tableWidget.currentRow()
        if selected_row == -1:
            return

        # Lấy mã đoàn viên từ hàng được chọn
        maDV = self.tableWidget.item(selected_row, 0).text()
        hoTen = self.tableWidget.item(selected_row, 1).text()

        # Hiển thị hộp thông báo xác nhận
        reply = QMessageBox.question(self, 'Xác nhận xóa', f'Bạn có chắc chắn muốn xóa đoàn viên {hoTen}?',
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            # Thực hiện xóa đoàn viên trong cơ sở dữ liệu
            query = "DELETE FROM doanvien WHERE maDV = %s"
            self.cursor.execute(query, (maDV,))
            self.conn.commit()

            # Cập nhật lại danh sách đoàn viên
            self.load_data()

    def add_member(self):
        """Mở form thêm đoàn viên."""
        self.add_form = AddDVForm()
        self.add_form.pushButton.clicked.connect(self.save_member)
        self.add_form.show()

    def edit_member(self):
        """Mở form sửa đoàn viên."""
        selected_row = self.tableWidget.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn một đoàn viên để sửa.")
            return

        # Lấy thông tin đoàn viên từ hàng được chọn
        maDV = self.tableWidget.item(selected_row, 0).text()
        hoTen = self.tableWidget.item(selected_row, 1).text()
        ngaySinh = self.tableWidget.item(selected_row, 2).text()
        gioiTinh = self.tableWidget.item(selected_row, 3).text()
        chiDoan = self.tableWidget.item(selected_row, 4).text()
        khoa = self.tableWidget.item(selected_row, 5).text()
        khoaHoc = self.tableWidget.item(selected_row, 6).text()
        chucVu = self.tableWidget.item(selected_row, 7).text()
        sdt = self.tableWidget.item(selected_row, 8).text()
        diaChi = self.tableWidget.item(selected_row, 9).text()

        # Mở form sửa đoàn viên và điền thông tin
        self.add_form = AddDVForm()
        self.add_form.txtMaDoanVien.setText(maDV)
        self.add_form.txtTen.setText(hoTen)
        self.add_form.NgaySinh.setDate(QDate.fromString(ngaySinh, "yyyy-MM-dd"))
        self.add_form.GioiTinh.setCurrentText(gioiTinh)
        self.add_form.txtChiDoan.setText(chiDoan)
        self.add_form.txtKhoa.setText(khoa)
        self.add_form.txtKhoaHoc.setText(khoaHoc)
        self.add_form.cbbChucVu.setCurrentText(chucVu)
        self.add_form.txtSDT.setText(sdt)
        self.add_form.txtDiaChi.setText(diaChi)

        self.add_form.pushButton.clicked.connect(self.save_member)
        self.add_form.show()

    def save_member(self):
        """Lưu thông tin đoàn viên vào cơ sở dữ liệu."""
        if not self.conn:
            return

        try:
            # Sử dụng toPlainText() thay vì text() cho QTextEdit
            maDV = self.add_form.txtMaDoanVien.toPlainText()
            hoTen = self.add_form.txtTen.toPlainText()
            ngaySinh = self.add_form.NgaySinh.date().toString("yyyy-MM-dd")
            gioiTinh = self.add_form.GioiTinh.currentText()
            chiDoan = self.add_form.txtChiDoan.toPlainText()
            khoa = self.add_form.txtKhoa.toPlainText()
            khoaHoc = self.add_form.txtKhoaHoc.toPlainText()
            chucVu = self.add_form.cbbChucVu.currentText()
            sdt = self.add_form.txtSDT.toPlainText()
            diaChi = self.add_form.txtDiaChi.toPlainText()

            # Kiểm tra xem là thêm mới hay sửa
            query = "SELECT maDV FROM doanvien WHERE maDV = %s"
            self.cursor.execute(query, (maDV,))
            existing_member = self.cursor.fetchone()

            if existing_member:
                # Sửa đoàn viên
                query = """
                    UPDATE doanvien 
                    SET hoTen = %s, ngaySinh = %s, gioiTinh = %s, chiDoan = %s, khoa = %s, khoaHoc = %s, chucVu = %s, sdt = %s, diaChi = %s
                    WHERE maDV = %s
                """
                self.cursor.execute(query, (hoTen, ngaySinh, gioiTinh, chiDoan, khoa, khoaHoc, chucVu, sdt, diaChi, maDV))
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setWindowTitle("Thành công")
                msg.setText("Cập nhật thông tin đoàn viên thành công!")
                msg.exec_()

            else:
                # Thêm đoàn viên mới
                query = """
                    INSERT INTO doanvien (maDV, hoTen, ngaySinh, gioiTinh, chiDoan, khoa, khoaHoc, chucVu, sdt, diaChi) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                self.cursor.execute(query, (maDV, hoTen, ngaySinh, gioiTinh, chiDoan, khoa, khoaHoc, chucVu, sdt, diaChi))
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setWindowTitle("Thành công")
                msg.setText("Thêm đoàn viên thành công!")
                msg.exec_()

            self.conn.commit()
            self.load_data()
            self.add_form.close()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Đã xảy ra lỗi: {str(e)}")

    def closeEvent(self, event):
        """Đóng kết nối cơ sở dữ liệu khi đóng ứng dụng"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QLDV()
    window.show()
    sys.exit(app.exec_())