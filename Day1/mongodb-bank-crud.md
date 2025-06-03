
# 📘 Quản lý dữ liệu khách hàng ngân hàng với MongoDB CRUD

## 🧩 1. Tổng quan MongoDB

### MongoDB là gì?
- **NoSQL**: Không dùng bảng như SQL mà lưu dữ liệu dưới dạng tài liệu (document).

- **Document**-based: Dữ liệu lưu dưới dạng BSON (JSON mở rộng).

- **Schema-less**: Không cần định nghĩa trước cấu trúc dữ liệu, linh hoạt khi dữ liệu thay đổi.

- **Ưu điểm cho hệ thống ngân hàng**:

      + Dễ dàng mở rộng khi số lượng khách hàng và giao dịch tăng.

      + Thích hợp cho dữ liệu không đồng nhất giữa các khách hàng.

      + Tốc độ truy xuất nhanh, phù hợp hệ thống real-time.

## ⚙️ 2. Cài đặt MongoDB

### Windows/macOS/Linux:
- Tải MongoDB tại: https://www.mongodb.com/try/download/community
- Cài đặt MongoDB Compass (giao diện GUI): https://www.mongodb.com/try/download/compass
- Khởi động MongoDB Shell (mongosh):

### Kết nối bằng mongosh:
``` bash
mongosh
```

---

## 🗃️ 3. Quản lý Database và Collection

### Tạo database và collections:
``` 
use banking_system
db.createCollection("customers")
db.createCollection("transactions")
```

### Xem danh sách:
``` 
show databases
use banking_system
show collections
```

### Sự khác biệt giữa Database, Collection, và Document trong MongoDB:
- **Database**: Tập hợp các collection.
- **Collection**: Tập hợp các documents.
- **Document**: Một bản ghi dữ liệu (kiểu ON).

---

## 📝 4. CRUD – Create (Thêm dữ liệu)

### Thêm 1 khách hàng:
```
db.customers.insertOne({
  customer_id: UUID("550e8400-e29b-41d4-a716-446655440000"),
  full_name: "Nguyen Van A",
  email: "nguyen@example.com",
  created_at: new ISODate("2024-01-01T00:00:00Z")
})
```

### Thêm nhiều giao dịch:
```
db.transactions.insertMany([
  {
    transaction_id: UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8"),
    customer_id: UUID("550e8400-e29b-41d4-a716-446655440000"),
    amount: 1000,
    type: "DEPOSIT",
    transaction_date: new ISODate("2024-02-01T10:00:00Z")
  },
  {
    transaction_id: UUID("6ba7b811-9dad-11d1-80b4-00c04fd430c8"),
    customer_id: UUID("550e8400-e29b-41d4-a716-446655440000"),
    amount: 500,
    type: "WITHDRAW",
    transaction_date: new ISODate("2024-02-02T12:00:00Z")
  }
])
```

---

## 🔍 5. CRUD – Read (Truy vấn dữ liệu)

### Tên khách hàng chứa "Nguyen":
```
db.customers.find({ full_name: { $regex: "Nguyen", $options: "i" } })
```

### Giao dịch đầu tiên có amount > 700:
```
db.transactions.findOne({ amount: { $gt: 700 } })
```

### Giao dịch amount >= 500 và type != "WITHDRAW":
```
db.transactions.find({
  amount: { $gte: 500 },
  type: { $ne: "WITHDRAW" }
})
```

### Khách hàng tạo trước ngày 01/06/2024:
```
db.customers.find({
  created_at: { $lt: new ISODate("2024-06-01T00:00:00Z") }
})
```

---

## ✏️ 6. CRUD – Update (Cập nhật dữ liệu)

### Cập nhật email khách hàng:
```
db.customers.updateOne(
  { customer_id: UUID("550e8400-e29b-41d4-a716-446655440000") },
  { $set: { email: "newemail@example.com" } }
)
```

### Thêm trường `status: "ACTIVE"` cho khách hàng tạo sau 01/01/2024:
```
db.customers.updateMany(
  { created_at: { $gt: new ISODate("2024-01-01T00:00:00Z") } },
  { $set: { status: "ACTIVE" } }
)
```

---

## 🗑️ 7. CRUD – Delete (Xóa dữ liệu)

### Xóa giao dịch theo transaction_id:
```
db.transactions.deleteOne({
  transaction_id: UUID("6ba7b811-9dad-11d1-80b4-00c04fd430c8")
})
```

---

## ⚙️ 8. Truy vấn với Query Operators

### `$eq` – Tên bằng:
```
db.customers.find({ full_name: { $eq: "Nguyen Van A" } })
```

### `$gt`, `$lte` – Amount > 300 và ngày <= 01/03/2024:
```
db.transactions.find({
  amount: { $gt: 300 },
  transaction_date: { $lte: new ISODate("2024-03-01T00:00:00Z") }
})
```

### `$ne` – Email khác "nguyen@example.com":
```
db.customers.find({ email: { $ne: "nguyen@example.com" } })
```

---
