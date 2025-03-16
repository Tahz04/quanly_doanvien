import mysql.connector
from PyQt5.QtWidgets import QApplication, QWidget, QTableWidgetItem, QMessageBox, QFileDialog
from PyQt5.uic import loadUi
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

class BaoCaoDoanVien(QWidget):
    def __init__(self):
        super().__init__()
        loadUi('BCTK.ui', self)
        self.conn = self.connect_db()
        if self.conn:
            self.cursor = self.conn.cursor()
        else:
            self.cursor = None
        self.load_data()
        self.load_nam_hoc_dv()  # Tải danh sách năm học vào combobox
        self.load_so_luong_dv()  # Tải số lượng đoàn viên ban đầu
        self.load_nam_hoc_hoat_dong()  # Tải năm học vào combobox hoạt động
        self.load_hoat_dong()  # Tải hoạt động ban đầu
        self.load_khoa()  # Tải danh sách khoa vào combobox
        self.btnXuatExcel.clicked.connect(self.xuat_excel)
        self.btnXuatPDF.clicked.connect(self.xuat_pdf)
        self.txtTimKiem.textChanged.connect(self.tim_kiem)
        self.cbbNamHocHD.currentIndexChanged.connect(self.load_hoat_dong)  # Khi chọn năm học, tải lại hoạt động
        self.cbbKhoa.currentIndexChanged.connect(self.filter_by_khoa)  # Khi chọn khoa, lọc đoàn viên
        self.cbbNamHocDV.currentIndexChanged.connect(self.load_so_luong_dv)  # Khi chọn năm học, tải lại số lượng đoàn viên

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

    def load_data(self):
        """Tải dữ liệu từ cơ sở dữ liệu và hiển thị lên bảng"""
        if self.conn is not None:
            self.cursor.execute("SELECT maDV, hoTen, khoa, chiDoan, chucVu FROM doanvien")
            rows = self.cursor.fetchall()
            self.tableDanhSachDV.setRowCount(len(rows))
            for i, row in enumerate(rows):
                for j, item in enumerate(row):
                    self.tableDanhSachDV.setItem(i, j, QTableWidgetItem(str(item)))

    def load_so_luong_dv(self):
        """Tải số lượng đoàn viên theo khoa và năm học được chọn, hiển thị lên bảng"""
        if self.conn is not None:
            nam_hoc = self.cbbNamHocDV.currentText()
            query = """
                SELECT khoa, COUNT(*) as so_luong 
                FROM doanvien 
                WHERE %s = 'Tất cả' OR khoaHoc = %s
                GROUP BY khoa
            """
            self.cursor.execute(query, (nam_hoc, nam_hoc))
            rows = self.cursor.fetchall()
            self.tableSoLuongDV.setRowCount(len(rows))
            for i, row in enumerate(rows):
                for j, item in enumerate(row):
                    self.tableSoLuongDV.setItem(i, j, QTableWidgetItem(str(item)))

    def load_nam_hoc_dv(self):
        """Tải danh sách năm học đoàn viên vào combobox"""
        if self.conn is not None:
            query = """
                SELECT DISTINCT khoaHoc 
                FROM doanvien 
                ORDER BY khoaHoc DESC
            """
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            self.cbbNamHocDV.clear()
            self.cbbNamHocDV.addItem("Tất cả")  # Thêm tùy chọn "Tất cả"
            for row in rows:
                self.cbbNamHocDV.addItem(row[0])

    def load_nam_hoc_hoat_dong(self):
        """Tải các năm học có hoạt động vào combobox"""
        if self.conn is not None:
            query = """
                SELECT DISTINCT YEAR(ngayToChuc) as nam_hoc 
                FROM hoatdong 
                ORDER BY nam_hoc DESC
            """
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            self.cbbNamHocHD.clear()
            for row in rows:
                self.cbbNamHocHD.addItem(str(row[0]))

    def load_hoat_dong(self):
        """Tải hoạt động theo năm học được chọn và hiển thị lên bảng"""
        if self.conn is not None:
            nam_hoc = self.cbbNamHocHD.currentText()
            query = """
                SELECT hd.tenHD, hd.ngayToChuc, COUNT(tg.maDV) as so_luong_tham_gia
                FROM hoatdong hd
                LEFT JOIN thamgiahoatdong tg ON hd.maHD = tg.maHD
                WHERE YEAR(hd.ngayToChuc) = %s
                GROUP BY hd.maHD
            """
            self.cursor.execute(query, (nam_hoc,))
            rows = self.cursor.fetchall()
            self.tableHoatDong.setRowCount(len(rows))
            for i, row in enumerate(rows):
                for j, item in enumerate(row):
                    self.tableHoatDong.setItem(i, j, QTableWidgetItem(str(item)))

    def load_khoa(self):
        """Tải danh sách khoa vào combobox"""
        if self.conn is not None:
            query = """
                SELECT DISTINCT khoa 
                FROM doanvien 
                ORDER BY khoa
            """
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            self.cbbKhoa.clear()
            self.cbbKhoa.addItem("Tất cả")  # Thêm tùy chọn "Tất cả"
            for row in rows:
                self.cbbKhoa.addItem(row[0])

    def filter_by_khoa(self):
        """Lọc đoàn viên theo khoa được chọn"""
        khoa = self.cbbKhoa.currentText()
        nam_hoc = self.cbbNamHocDV.currentText()
        self.filter_data(khoa, nam_hoc)

    def filter_data(self, khoa, nam_hoc):
        """Lọc dữ liệu đoàn viên dựa trên khoa và năm học"""
        if self.conn is not None:
            query = """
                SELECT maDV, hoTen, khoa, chiDoan, chucVu 
                FROM doanvien 
                WHERE (%s = 'Tất cả' OR khoa = %s)
                AND (%s = 'Tất cả' OR khoaHoc = %s)
            """
            self.cursor.execute(query, (khoa, khoa, nam_hoc, nam_hoc))
            rows = self.cursor.fetchall()
            self.tableDanhSachDV.setRowCount(len(rows))
            for i, row in enumerate(rows):
                for j, item in enumerate(row):
                    self.tableDanhSachDV.setItem(i, j, QTableWidgetItem(str(item)))

    def tim_kiem(self):
        """Tìm kiếm đoàn viên theo mã hoặc tên"""
        search_text = self.txtTimKiem.text()
        if self.conn is not None:
            query = "SELECT maDV, hoTen, khoa, chiDoan, chucVu FROM doanvien WHERE maDV LIKE %s OR hoTen LIKE %s"
            self.cursor.execute(query, (f"%{search_text}%", f"%{search_text}%"))
            rows = self.cursor.fetchall()
            self.tableDanhSachDV.setRowCount(len(rows))
            for i, row in enumerate(rows):
                for j, item in enumerate(row):
                    self.tableDanhSachDV.setItem(i, j, QTableWidgetItem(str(item)))

    def xuat_excel(self):
        """Xuất dữ liệu ra file Excel"""
        try:
            # Lấy dữ liệu từ bảng
            rows = self.tableDanhSachDV.rowCount()
            columns = self.tableDanhSachDV.columnCount()
            data = []
            for i in range(rows):
                row = []
                for j in range(columns):
                    item = self.tableDanhSachDV.item(i, j)
                    row.append(item.text() if item else "")
                data.append(row)

            # Tạo DataFrame từ dữ liệu
            df = pd.DataFrame(data, columns=["Mã ĐV", "Họ tên", "Khoa", "Chi đoàn", "Chức vụ"])

            # Xuất ra file Excel
            file_path, _ = QFileDialog.getSaveFileName(self, "Lưu file Excel", "", "Excel Files (*.xlsx)")
            if file_path:
                df.to_excel(file_path, index=False)
                QMessageBox.information(self, "Xuất Excel", "Xuất file Excel thành công!")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi xuất Excel: {str(e)}")

    def xuat_pdf(self):
        try:
            # Đăng ký font hỗ trợ tiếng Việt (Arial)
            pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))  # Đảm bảo file 'arial.ttf' có trong thư mục

            # Lấy dữ liệu từ bảng
            rows = self.tableDanhSachDV.rowCount()
            columns = self.tableDanhSachDV.columnCount()
            data = []
            for i in range(rows):
                row = []
                for j in range(columns):
                    item = self.tableDanhSachDV.item(i, j)
                    row.append(item.text() if item else "")
                data.append(row)

            # Tạo file PDF
            file_path, _ = QFileDialog.getSaveFileName(self, "Lưu file PDF", "", "PDF Files (*.pdf)")
            if file_path:
                c = canvas.Canvas(file_path, pagesize=letter)
                c.setFont("Arial", 12)  # Sử dụng font Arial
                y = 750  # Vị trí bắt đầu viết từ trên xuống

                # Viết tiêu đề cột
                headers = ["Mã ĐV", "Họ tên", "Khoa", "Chi đoàn", "Chức vụ"]
                header_line = " | ".join(headers)
                c.drawString(50, y, header_line)
                y -= 20  # Di chuyển xuống dòng tiếp theo

                # Viết dữ liệu từ bảng
                for row in data:
                    line = " | ".join(row)
                    c.drawString(50, y, line)
                    y -= 20  # Di chuyển xuống dòng tiếp theo
                    if y < 50:  # Nếu hết trang, tạo trang mới
                        c.showPage()
                        y = 750  # Đặt lại vị trí y cho trang mới

                c.save()  # Lưu file PDF
                QMessageBox.information(self, "Xuất PDF", "Xuất file PDF thành công!")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi xuất PDF: {str(e)}")

    def closeEvent(self, event):
        """Đóng kết nối cơ sở dữ liệu khi đóng ứng dụng"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        event.accept()


if __name__ == "__main__":
    app = QApplication([])
    window = BaoCaoDoanVien()
    window.show()
    app.exec_()