# Quản lý giao dịch thư viện với Transaction và Xử lý Lỗi trong MongoDB — Phần Lý Thuyết

## 1. ACID trong MongoDB

MongoDB hỗ trợ **multi-document transactions** bắt đầu từ phiên bản 4.0, đảm bảo tính **ACID** trong các giao dịch phức tạp trên nhiều document hoặc collection:

- **Atomicity (Tính nguyên tử):**  
  Tất cả các thao tác trong transaction được thực hiện thành công hoặc không thực hiện gì cả. Nếu có lỗi xảy ra, toàn bộ transaction sẽ rollback.

- **Consistency (Tính nhất quán):**  
  Dữ liệu luôn tuân theo các ràng buộc và trạng thái hợp lệ trước và sau khi transaction hoàn tất.

- **Isolation (Tính cô lập):**  
  Các transaction thực thi riêng biệt, các thay đổi chỉ được nhìn thấy khi transaction commit. MongoDB dùng **snapshot isolation** để đảm bảo.

- **Durability (Tính bền vững):**  
  Sau khi commit, dữ liệu được ghi chắc chắn vào ổ đĩa (tuỳ thuộc writeConcern), đảm bảo không mất dữ liệu dù sự cố hệ thống.

### Hạn chế của transaction trong MongoDB

- Transaction càng lớn, càng nhiều document, hiệu suất có thể giảm do tăng overhead quản lý transaction.
- Transaction không phù hợp để xử lý các thao tác đơn giản, khối lượng lớn với latency thấp.
- Nên thiết kế transaction nhỏ gọn, tránh giữ transaction quá lâu.

### Áp dụng hiệu quả trong thư viện số

- Chỉ dùng transaction cho các thao tác cần đảm bảo tính toàn vẹn, ví dụ: mượn sách (giảm stock + thêm record loans).
- Các thao tác không quan trọng hoặc đơn giản có thể dùng single document atomic operations để tăng tốc.

---

## 2. Transaction Options: readConcern và writeConcern

### readConcern

- `"local"`: Đọc dữ liệu đã ghi vào node local, có thể chưa đồng bộ với replica set.
- `"majority"`: Đọc dữ liệu đã được ghi và đồng bộ đến đa số node replica.
- `"snapshot"`: Đảm bảo tất cả các thao tác trong transaction nhìn thấy cùng một snapshot dữ liệu tại thời điểm transaction bắt đầu. Cần dùng trong multi-document transactions để đảm bảo tính nhất quán.

### writeConcern

- `"1"`: Xác nhận ghi thành công trên node primary.
- `"majority"`: Xác nhận ghi thành công trên đa số node replica set, tăng tính an toàn.
- `{ wtimeout: 5000 }`: Giới hạn thời gian ghi (5 giây). Nếu không hoàn thành ghi trong thời gian này sẽ báo lỗi timeout.

### Ví dụ trong hệ thống thư viện

- Transaction mượn sách sử dụng  
  ```json
  {
    readConcern: "snapshot",
    writeConcern: { w: "majority", wtimeout: 5000 }
  }
