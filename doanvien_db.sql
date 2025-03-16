-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Máy chủ: 127.0.0.1
-- Thời gian đã tạo: Th3 16, 2025 lúc 04:46 PM
-- Phiên bản máy phục vụ: 10.4.32-MariaDB
-- Phiên bản PHP: 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Cơ sở dữ liệu: `doanvien_db`
--

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `doanphi`
--

CREATE TABLE `doanphi` (
  `maDP` int(11) NOT NULL,
  `maDV` int(11) DEFAULT NULL,
  `soTien` decimal(10,2) NOT NULL,
  `ngayNop` date DEFAULT NULL,
  `ghiChu` text DEFAULT NULL,
  `trangThai` varchar(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Đang đổ dữ liệu cho bảng `doanphi`
--

INSERT INTO `doanphi` (`maDP`, `maDV`, `soTien`, `ngayNop`, `ghiChu`, `trangThai`) VALUES
(1, 1, 710000.00, '2025-03-13', NULL, 'Đã nộp'),
(2, 2, 100000.00, '2025-03-08', '', 'Đã nộp'),
(3, 3, 50000.00, '2024-03-10', 'Nộp phí định kỳ', 'Đã nộp'),
(4, 3, 50000.00, '2000-01-01', 'Nộp phí định kì', 'Đã nộp'),
(5, 5, 50000.00, '2000-01-01', 'Nộp phí định kỳ', 'Đã nộp'),
(6, 1, 50000.00, '2025-03-13', 'phí', 'Đã nộp'),
(7, 3, 50000.00, '2025-03-13', 'phí', 'Đã nộp'),
(8, 6, 50000.00, '2025-03-13', 'test', 'Đã nộp'),
(9, 4, 50000.00, '2025-03-07', 'test', 'Đã nộp'),
(10, 2, 50000.00, NULL, 'abc', 'Chưa nộp'),
(11, 4, 10000.00, NULL, '', 'Chưa nộp');

--
-- Bẫy `doanphi`
--
DELIMITER $$
CREATE TRIGGER `update_trangThai_on_insert` BEFORE INSERT ON `doanphi` FOR EACH ROW BEGIN
    IF NEW.ngayNop IS NOT NULL THEN
        SET NEW.trangThai = 'Đã nộp';
    ELSE
        SET NEW.trangThai = 'Chưa nộp';
    END IF;
END
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `update_trangThai_on_update` BEFORE UPDATE ON `doanphi` FOR EACH ROW BEGIN
    IF NEW.ngayNop IS NOT NULL THEN
        SET NEW.trangThai = 'Đã nộp';
    ELSE
        SET NEW.trangThai = 'Chưa nộp';
    END IF;
END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `doanvien`
--

CREATE TABLE `doanvien` (
  `maDV` int(11) NOT NULL,
  `hoTen` varchar(100) NOT NULL,
  `ngaySinh` date NOT NULL,
  `gioiTinh` enum('Nam','Nữ','Khác') NOT NULL,
  `chiDoan` varchar(50) DEFAULT NULL,
  `khoa` varchar(50) DEFAULT NULL,
  `khoaHoc` varchar(20) DEFAULT NULL,
  `chucVu` enum('Bí thư','Phó Bí thư','Ủy viên','Đoàn viên') DEFAULT 'Đoàn viên',
  `sdt` varchar(15) DEFAULT NULL,
  `diaChi` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Đang đổ dữ liệu cho bảng `doanvien`
--

INSERT INTO `doanvien` (`maDV`, `hoTen`, `ngaySinh`, `gioiTinh`, `chiDoan`, `khoa`, `khoaHoc`, `chucVu`, `sdt`, `diaChi`) VALUES
(1, 'Nguyễn Văn A', '2001-05-10', 'Nam', 'Chi đoàn 1', 'Công nghệ thông tin', 'K15', 'Bí thư', '0987654321', 'Hà Nội'),
(2, 'Trần Thị B', '2002-08-15', 'Nữ', 'Chi đoàn 2', 'Quản trị kinh doanh', 'K16', 'Đoàn viên', '0978123456', 'Hồ Chí Minh'),
(3, 'Dương Văn Thành', '2004-12-15', 'Nam', 'Chi đoàn 6', 'Công nghệ thông tin', 'K13', 'Đoàn viên', '08988', 'Hưng Yên'),
(4, 'Long Phương T', '2000-01-01', 'Nữ', 'Chi đoàn 6', 'Công nghệ thông tin', 'K13', 'Bí thư', '0266556', 'Hà Giang'),
(5, 'Nguyễn Thạc T', '2000-01-01', 'Nam', 'Chi đoàn 6', 'Công nghệ thông tin', 'K13', 'Đoàn viên', '0156', 'Bắc Ninh'),
(6, 'Nguyễn Duy A', '2000-01-01', 'Nam', 'Chi đoàn 4', 'Kinh tế', 'K13', 'Đoàn viên', '021566', 'Vĩnh Phúc'),
(7, 'Trần Đức H', '2005-11-25', 'Nam', 'ITCI', 'Công nghệ thông tin', 'K14', 'Đoàn viên', '125125', 'Hưng Yên');

--
-- Bẫy `doanvien`
--
DELIMITER $$
CREATE TRIGGER `before_delete_doanvien` BEFORE DELETE ON `doanvien` FOR EACH ROW BEGIN
    IF (SELECT COUNT(*) FROM thamgiahoatdong WHERE maDV = OLD.maDV) > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Không thể xóa đoàn viên vì đang tham gia hoạt động.';
    END IF;
    IF (SELECT COUNT(*) FROM doanphi WHERE maDV = OLD.maDV) > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Không thể xóa đoàn viên vì có lịch sử đóng đoàn phí.';
    END IF;
END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `hoatdong`
--

CREATE TABLE `hoatdong` (
  `maHD` int(11) NOT NULL,
  `tenHD` varchar(255) NOT NULL,
  `ngayToChuc` date NOT NULL,
  `diaDiem` varchar(255) DEFAULT NULL,
  `noiDung` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Đang đổ dữ liệu cho bảng `hoatdong`
--

INSERT INTO `hoatdong` (`maHD`, `tenHD`, `ngayToChuc`, `diaDiem`, `noiDung`) VALUES
(1, 'Chiến dịch Mùa hè xanh', '2024-07-15', 'Xã A, Tỉnh B', 'Hoạt động tình nguyện giúp đỡ cộng đồng'),
(2, 'Hiến máu nhân đạoo', '2024-06-10', 'Bệnh viện TW', 'Chương trình hiến máu cứu người'),
(3, 'test', '2000-01-01', 'test', 'test'),
(4, 'test', '2000-01-01', 'test', 'test');

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `thamgiahoatdong`
--

CREATE TABLE `thamgiahoatdong` (
  `maDV` int(11) NOT NULL,
  `maHD` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Đang đổ dữ liệu cho bảng `thamgiahoatdong`
--

INSERT INTO `thamgiahoatdong` (`maDV`, `maHD`) VALUES
(1, 1),
(1, 2),
(2, 1),
(2, 2),
(2, 3),
(3, 2),
(3, 3),
(4, 1),
(5, 1),
(5, 2);

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `thongke_doanphi`
--

CREATE TABLE `thongke_doanphi` (
  `namHoc` varchar(9) NOT NULL,
  `tongThu` decimal(15,2) DEFAULT 0.00,
  `tongChi` decimal(15,2) DEFAULT 0.00
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Đang đổ dữ liệu cho bảng `thongke_doanphi`
--

INSERT INTO `thongke_doanphi` (`namHoc`, `tongThu`, `tongChi`) VALUES
('2023-2024', 1000000.00, 200000.00);

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `username` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Đang đổ dữ liệu cho bảng `users`
--

INSERT INTO `users` (`id`, `username`, `password`) VALUES
(1, 'dvt', '1512');

--
-- Chỉ mục cho các bảng đã đổ
--

--
-- Chỉ mục cho bảng `doanphi`
--
ALTER TABLE `doanphi`
  ADD PRIMARY KEY (`maDP`),
  ADD KEY `maDV` (`maDV`);

--
-- Chỉ mục cho bảng `doanvien`
--
ALTER TABLE `doanvien`
  ADD PRIMARY KEY (`maDV`);

--
-- Chỉ mục cho bảng `hoatdong`
--
ALTER TABLE `hoatdong`
  ADD PRIMARY KEY (`maHD`);

--
-- Chỉ mục cho bảng `thamgiahoatdong`
--
ALTER TABLE `thamgiahoatdong`
  ADD PRIMARY KEY (`maDV`,`maHD`),
  ADD KEY `maHD` (`maHD`);

--
-- Chỉ mục cho bảng `thongke_doanphi`
--
ALTER TABLE `thongke_doanphi`
  ADD PRIMARY KEY (`namHoc`);

--
-- Chỉ mục cho bảng `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT cho các bảng đã đổ
--

--
-- AUTO_INCREMENT cho bảng `doanphi`
--
ALTER TABLE `doanphi`
  MODIFY `maDP` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- AUTO_INCREMENT cho bảng `doanvien`
--
ALTER TABLE `doanvien`
  MODIFY `maDV` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT cho bảng `hoatdong`
--
ALTER TABLE `hoatdong`
  MODIFY `maHD` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT cho bảng `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- Các ràng buộc cho các bảng đã đổ
--

--
-- Các ràng buộc cho bảng `doanphi`
--
ALTER TABLE `doanphi`
  ADD CONSTRAINT `doanphi_ibfk_1` FOREIGN KEY (`maDV`) REFERENCES `doanvien` (`maDV`) ON DELETE CASCADE;

--
-- Các ràng buộc cho bảng `thamgiahoatdong`
--
ALTER TABLE `thamgiahoatdong`
  ADD CONSTRAINT `thamgiahoatdong_ibfk_1` FOREIGN KEY (`maDV`) REFERENCES `doanvien` (`maDV`) ON DELETE CASCADE,
  ADD CONSTRAINT `thamgiahoatdong_ibfk_2` FOREIGN KEY (`maHD`) REFERENCES `hoatdong` (`maHD`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
