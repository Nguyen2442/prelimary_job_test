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