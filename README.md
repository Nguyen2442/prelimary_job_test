<!-- fullWidth: false tocVisible: false tableWrap: true -->
# prelimary job test API

## Structure

CDMS có 3 đầu input:

- webhook: client đẩy json vào
- excel: client upload file vào
- Poll: Cmds tự gọi api get product của vietful sau mỗi 15 giây

3 service chính:

- vietful_emulator: giả lập kho hàng bằng faker, có api danh sách sản phẩm để CMDS poll và api để tạo thay đổi
- CDMS: nhận dữ liệu qua 3 cơ chế (poll, webhook, Excel), so hash để chỉ lưu dữ liệu mới vào Postgres theo kiểu exactly-once, và chịu được khi một service khác gặp sự cố.
- clients: chứa script giả lập hệ thống bên ngoài đẩy dữ liệu vào CDMS, gồm webhook và upload Excel ( chứa script chạy ngoài docker, không phải service )

## Database schema

Postgres, bảng tự tạo khi CDMS khởi động (xem cdms/app/models.py).

### product_state

Trạng thái mới nhất của mỗi SKU.

| Cột | Kiểu | Ghi chú |
| --- | --- | --- |
| sku | varchar | khóa chính |
| data | jsonb | nội dung sản phẩm |
| source_updated_at | timestamp | lastUpdatedDate từ nguồn |
| version | int | tăng mỗi lần dữ liệu đổi |

### change_log

Lịch sử thay đổi, mỗi version của một SKU là một dòng.

| Cột | Kiểu | Ghi chú |
| --- | --- | --- |
| id | serial | khóa chính |
| sku | varchar | có index |
| version | int | unique cùng sku |
| source | varchar | POLL, WEBHOOK hoặc EXCEL |
| data | jsonb | nội dung tại version đó |
| source_updated_at | timestamp | lastUpdatedDate từ nguồn |
| recorded_at | timestamp | thời điểm CDMS ghi |

### Quy tắc ghi

- SKU mới: tạo version 1
- Dữ liệu cũ hơn bản đang lưu: bỏ qua
- Dữ liệu không đổi: bỏ qua
- Còn lại: cập nhật và tăng version

Mỗi lần ghi đều thêm một dòng vào change_log.
