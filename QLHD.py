import sys
import mysql.connector
from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QWidget, QMessageBox
from PyQt5.uic import loadUi


class AddHDForm(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi("AddHD.ui", self)


class QLHD(QMainWindow):
    def __init__(self):
        super(QLHD, self).__init__()
        loadUi("QLHD.ui", self)  # Load giao diện từ file QLHD.ui

        # Kết nối sự kiện
        self.tableHoatDong.itemSelectionChanged.connect(self.load_doan_vien)
        self.btnTimKiem.clicked.connect(self.search_hoat_dong)
        self.btnXoa.clicked.connect(self.xoa_hoat_dong)
        self.btnXoaDV.clicked.connect(self.xoa_doan_vien)
        self.btnThemDV.clicked.connect(self.them_doan_vien)  # Kết nối sự kiện thêm đoàn viên
        self.btnThem.clicked.connect(self.add_HD)  # Thêm sự kiện thêm hoạt động
        self.btnSua.clicked.connect(self.edit_HD)  # Thêm sự kiện sửa hoạt động
        self.on_table_item_selection()  # Đảm bảo nút được disable khi mở giao diện
        self.tableHoatDong.itemSelectionChanged.connect(self.on_table_item_selection)
        self.tableDoanVien.itemSelectionChanged.connect(self.on_table_item_selection)


        # Kết nối cơ sở dữ liệu và khởi tạo cursor
        self.conn = self.connect_db()
        if self.conn:
            self.cursor = self.conn.cursor()
        else:
            self.cursor = None

        # Load dữ liệu khi khởi động
        self.load_hoat_dong()

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

    def search_hoat_dong(self):
        """Tìm kiếm hoạt động theo mã hoặc tên."""
        keyword = self.txtTimKiem.text().strip()  # Lấy từ khóa tìm kiếm và loại bỏ khoảng trắng thừa
        if not keyword:
            self.load_hoat_dong()  # Nếu không có từ khóa, tải lại toàn bộ dữ liệu
            return

        try:
            # Câu truy vấn SQL để tìm kiếm hoạt động
            query = """
                SELECT maHD, tenHD, ngayToChuc, diaDiem, noiDung 
                FROM hoatdong 
                WHERE maHD LIKE %s OR tenHD LIKE %s
            """
            self.cursor.execute(query, (f'%{keyword}%', f'%{keyword}%'))  # Thực thi truy vấn
            rows = self.cursor.fetchall()  # Lấy tất cả kết quả

            # Hiển thị kết quả lên bảng
            self.tableHoatDong.setRowCount(len(rows))  # Đặt số hàng của bảng
            for row_idx, row_data in enumerate(rows):
                for col_idx, col_data in enumerate(row_data):
                    # Đặt dữ liệu vào từng ô trong bảng
                    self.tableHoatDong.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))
        except Exception as e:
            print(f"Lỗi khi tìm kiếm hoạt động: {e}")  # Xử lý ngoại lệ nếu có lỗi

    def load_hoat_dong(self):
        """Hiển thị danh sách hoạt động trong bảng tableHoatDong"""
        if not self.conn:
            return

        cursor = self.conn.cursor()
        query = "SELECT maHD, tenHD, ngayToChuc, diaDiem, noiDung FROM hoatdong"
        cursor.execute(query)
        rows = cursor.fetchall()

        self.tableHoatDong.setRowCount(len(rows))
        self.tableHoatDong.setColumnCount(5)
        self.tableHoatDong.setHorizontalHeaderLabels(["ID", "Tên hoạt động", "Ngày tổ chức", "Địa điểm", "Nội dung"])

        for row_idx, row_data in enumerate(rows):
            for col_idx, value in enumerate(row_data):
                self.tableHoatDong.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

        cursor.close()

    def load_doan_vien(self):
        """Khi chọn 1 hoạt động, hiển thị danh sách đoàn viên tham gia. Nếu không chọn, reset bảng tableDoanVien."""
        selected_row = self.tableHoatDong.currentRow()

        # Nếu không có hàng nào được chọn, reset bảng tableDoanVien
        if selected_row == -1:
            self.tableDoanVien.setRowCount(0)
            self.tableDoanVien.setColumnCount(5)
            self.tableDoanVien.setHorizontalHeaderLabels(["Mã Đoàn Viên", "Họ tên", "Khoa", "Chi đoàn", "Khóa học"])
            return

        # Lấy mã hoạt động từ hàng được chọn
        idHD = self.tableHoatDong.item(selected_row, 0).text().strip()

        if not self.conn:
            return

        cursor = self.conn.cursor()
        query = """
            SELECT d.maDV, d.hoTen, d.chiDoan, d.khoa, d.khoaHoc
            FROM doanvien d
            JOIN thamgiahoatdong t ON d.maDV = t.maDV
            WHERE t.maHD = %s
        """
        cursor.execute(query, (idHD,))
        rows = cursor.fetchall()

        # Xóa dữ liệu cũ trước khi cập nhật
        self.tableDoanVien.setRowCount(0)

        # Đặt lại số hàng và cột
        self.tableDoanVien.setRowCount(len(rows))
        self.tableDoanVien.setColumnCount(5)
        self.tableDoanVien.setHorizontalHeaderLabels(["Mã Đoàn Viên", "Họ tên", "Khoa", "Chi đoàn", "Khóa học"])

        # Đổ dữ liệu vào bảng
        for row_idx, row_data in enumerate(rows):
            for col_idx, value in enumerate(row_data):
                self.tableDoanVien.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

        cursor.close()

    def xoa_hoat_dong(self):
        """Xóa hoạt động đang chọn."""
        selected_row = self.tableHoatDong.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn một hoạt động để xóa!")
            return

        # Lấy mã hoạt động từ hàng được chọn
        maHD = self.tableHoatDong.item(selected_row, 0).text().strip()

        # Hiển thị hộp thoại xác nhận
        reply = QMessageBox.question(
            self, "Xác nhận", "Bạn có chắc chắn muốn xóa hoạt động này không?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                # Xóa các bản ghi liên quan trong bảng thamgiahoatdong trước
                query_delete_thamgia = "DELETE FROM thamgiahoatdong WHERE maHD = %s"
                self.cursor.execute(query_delete_thamgia, (maHD,))
                self.conn.commit()

                # Xóa hoạt động từ bảng hoatdong
                query_delete_hoatdong = "DELETE FROM hoatdong WHERE maHD = %s"
                self.cursor.execute(query_delete_hoatdong, (maHD,))
                self.conn.commit()

                # Cập nhật lại bảng hiển thị
                self.load_hoat_dong()
                QMessageBox.information(self, "Thông báo", "Xóa hoạt động thành công!")
            except Exception as e:
                print(f"Lỗi khi xóa hoạt động: {e}")
                QMessageBox.critical(self, "Lỗi", "Không thể xóa hoạt động!")

    def on_table_item_selection(self):
        has_selection = len(self.tableHoatDong.selectedItems()) > 0
        self.btnSua.setEnabled(has_selection)
        self.btnXoa.setEnabled(has_selection)
        has_selection = len(self.tableDoanVien.selectedItems()) > 0
        self.btnXoaDV.setEnabled(has_selection)

    def them_doan_vien(self):
        """Thêm đoàn viên vào hoạt động đang chọn."""
        # Lấy mã hoặc tên đoàn viên từ txtThemDV
        keyword = self.txtThemDV.text().strip()
        if not keyword:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập mã hoặc tên đoàn viên!")
            return

        # Lấy mã hoạt động đang được chọn
        selected_row_hd = self.tableHoatDong.currentRow()
        if selected_row_hd == -1:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn một hoạt động!")
            return
        maHD = self.tableHoatDong.item(selected_row_hd, 0).text().strip()

        # Tìm đoàn viên theo mã hoặc tên
        try:
            query_find_dv = """
                SELECT maDV FROM doanvien 
                WHERE maDV = %s OR hoTen LIKE %s
            """
            self.cursor.execute(query_find_dv, (keyword, f'%{keyword}%'))
            result = self.cursor.fetchone()

            if not result:
                QMessageBox.warning(self, "Cảnh báo", "Không tìm thấy đoàn viên!")
                return

            maDV = result[0]  # Lấy mã đoàn viên

            # Kiểm tra xem đoàn viên đã tham gia hoạt động chưa
            query_check = """
                SELECT * FROM thamgiahoatdong 
                WHERE maHD = %s AND maDV = %s
            """
            self.cursor.execute(query_check, (maHD, maDV))
            if self.cursor.fetchone():
                QMessageBox.warning(self, "Cảnh báo", "Đoàn viên đã tham gia hoạt động này!")
                return

            # Thêm đoàn viên vào hoạt động
            query_insert = """
                INSERT INTO thamgiahoatdong (maHD, maDV) 
                VALUES (%s, %s)
            """
            self.cursor.execute(query_insert, (maHD, maDV))
            self.conn.commit()

            # Cập nhật lại danh sách đoàn viên tham gia
            self.load_doan_vien()
            QMessageBox.information(self, "Thông báo", "Thêm đoàn viên thành công!")
        except Exception as e:
            print(f"Lỗi khi thêm đoàn viên: {e}")
            QMessageBox.critical(self, "Lỗi", "Không thể thêm đoàn viên!")

    def xoa_doan_vien(self):
        """Xóa đoàn viên tham gia hoạt động đang chọn."""
        selected_row_dv = self.tableDoanVien.currentRow()
        selected_row_hd = self.tableHoatDong.currentRow()

        if selected_row_dv == -1 or selected_row_hd == -1:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn một đoàn viên và hoạt động để xóa!")
            return

        # Lấy mã đoàn viên và mã hoạt động
        maDV = self.tableDoanVien.item(selected_row_dv, 0).text().strip()
        maHD = self.tableHoatDong.item(selected_row_hd, 0).text().strip()

        # Hiển thị hộp thoại xác nhận
        reply = QMessageBox.question(
            self, "Xác nhận", "Bạn có chắc chắn muốn xóa đoàn viên này khỏi hoạt động không?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                # Xóa đoàn viên khỏi hoạt động trong bảng thamgiahoatdong
                query_delete = "DELETE FROM thamgiahoatdong WHERE maHD = %s AND maDV = %s"
                self.cursor.execute(query_delete, (maHD, maDV))
                self.conn.commit()

                # Cập nhật lại danh sách đoàn viên
                self.load_doan_vien()
                QMessageBox.information(self, "Thông báo", "Xóa đoàn viên khỏi hoạt động thành công!")
            except Exception as e:
                print(f"Lỗi khi xóa đoàn viên: {e}")
                QMessageBox.critical(self, "Lỗi", "Không thể xóa đoàn viên khỏi hoạt động!")

    def add_HD(self):
        """Mở form thêm hoạt động."""
        try:
            self.add_form = AddHDForm()  # Khởi tạo form
            self.add_form.pushButton.clicked.connect(self.save_HD)  # Kết nối sự kiện nút "Xác nhận"
            self.add_form.show()  # Hiển thị form
        except Exception as e:
            print(f"Lỗi khi mở form thêm hoạt động: {e}")
            QMessageBox.critical(self, "Lỗi", "Không thể mở form thêm hoạt động!")

    def edit_HD(self):
        """Mở form sửa hoạt động."""
        try:
            selected_row = self.tableHoatDong.currentRow()  # Lấy hàng được chọn
            if selected_row == -1:
                QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn một hoạt động để sửa.")
                return

            # Lấy thông tin hoạt động từ bảng
            maHD = self.tableHoatDong.item(selected_row, 0).text()
            tenHD = self.tableHoatDong.item(selected_row, 1).text()
            ngayToChuc = self.tableHoatDong.item(selected_row, 2).text()
            diaDiem = self.tableHoatDong.item(selected_row, 3).text()
            noiDung = self.tableHoatDong.item(selected_row, 4).text()

            # Mở form sửa
            self.add_form = AddHDForm()
            self.add_form.txtID.setText(maHD)
            self.add_form.txtTen.setText(tenHD)
            self.add_form.dateEdit.setDate(QDate.fromString(ngayToChuc, "yyyy-MM-dd"))
            self.add_form.txtDiaDiem.setText(diaDiem)
            self.add_form.txtNoiDung.setPlainText(noiDung)  # Sửa thành QTextEdit

            self.add_form.pushButton.clicked.connect(self.save_HD)  # Kết nối sự kiện nút "Xác nhận"
            self.add_form.show()
        except Exception as e:
            print(f"Lỗi khi mở form sửa hoạt động: {e}")
            QMessageBox.critical(self, "Lỗi", "Không thể mở form sửa hoạt động!")

    def save_HD(self):
        """Lưu thông tin hoạt động vào cơ sở dữ liệu."""
        try:
            # Lấy dữ liệu từ form
            maHD = self.add_form.txtID.text().strip()
            tenHD = self.add_form.txtTen.text().strip()
            ngayToChuc = self.add_form.dateEdit.date().toString("yyyy-MM-dd")
            diaDiem = self.add_form.txtDiaDiem.text().strip()
            noiDung = self.add_form.txtNoiDung.toPlainText().strip()  # Sửa thành QTextEdit

            query = "SELECT maHD FROM hoatdong WHERE maHD = %s"
            self.cursor.execute(query, (maHD,))
            maHD = self.cursor.fetchone()

            # Kiểm tra dữ liệu đầu vào
            if not tenHD or not diaDiem or not noiDung:
                QMessageBox.warning(self, "Cảnh báo", "Vui lòng điền đầy đủ thông tin!")
                return

            # Kiểm tra xem là thêm mới hay sửa
            if maHD:  # Nếu có mã hoạt động, thực hiện cập nhật
                query = """
                    UPDATE hoatdong 
                    SET tenHD = %s, ngayToChuc = %s, diaDiem = %s, noiDung = %s
                    WHERE maHD = %s
                """
                self.cursor.execute(query, (tenHD, ngayToChuc, diaDiem, noiDung, maHD))
                QMessageBox.information(self, "Thành công", "Cập nhật thông tin hoạt động thành công!")
            else:  # Thêm mới hoạt động
                query = """
                    INSERT INTO hoatdong (tenHD, ngayToChuc, diaDiem, noiDung) 
                    VALUES (%s, %s, %s, %s)
                """
                self.cursor.execute(query, (tenHD, ngayToChuc, diaDiem, noiDung))
                QMessageBox.information(self, "Thành công", "Thêm hoạt động thành công!")

            self.conn.commit()  # Lưu thay đổi vào database
            self.load_hoat_dong()  # Cập nhật lại danh sách
            self.add_form.close()  # Đóng form
        except Exception as e:
            print(f"Lỗi khi lưu hoạt động: {e}")
            QMessageBox.critical(self, "Lỗi", f"Không thể lưu hoạt động: {str(e)}")

    def closeEvent(self, event):
        """Đóng kết nối cơ sở dữ liệu khi đóng ứng dụng"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QLHD()
    window.show()
    sys.exit(app.exec_())