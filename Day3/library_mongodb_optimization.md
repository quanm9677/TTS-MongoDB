
# Tối ưu hóa quản lý dữ liệu thư viện với MongoDB

---

## 1. Dữ liệu mẫu

### Collection: `members`
```json
{
  "member_id": UUID("550e8400-e29b-41d4-a716-446655440000"),
  "full_name": "Nguyen Thi B",
  "email": "nguyenb@example.com",
  "joined_at": ISODate("2024-03-15T00:00:00Z")
}
```

### Collection: `loans`
```json
{
  "loan_id": UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8"),
  "member_id": UUID("550e8400-e29b-41d4-a716-446655440000"),
  "book_id": UUID("7ca7b810-9dad-11d1-80b4-00c04fd430c8"),
  "book_title": "Dune",
  "borrow_date": ISODate("2024-04-01T00:00:00Z"),
  "due_date": ISODate("2024-04-15T00:00:00Z")
}
```

### Collection: `audit_logs` (dữ liệu tạm thời)
```json
{
  "log_id": UUID("8da7b810-9dad-11d1-80b4-00c04fd430c8"),
  "action": "BORROW",
  "member_id": UUID("550e8400-e29b-41d4-a716-446655440000"),
  "created_at": ISODate("2024-04-01T00:00:00Z")
}
```

---

## 2. Tạo và quản lý Indexes

### 2.1 Tạo Single Field Index trên `email` trong `members`
```js
db.members.createIndex({ email: 1 })
```

### 2.2 Tạo Compound Index trên `member_id` và `borrow_date` trong `loans`
```js
db.loans.createIndex({ member_id: 1, borrow_date: -1 })
```

### 2.3 Xóa chỉ mục trên `email`
```js
db.members.dropIndex("email_1")
```

### 2.4 Kiểm tra hiệu quả chỉ mục với `explain()`
```js
db.loans.find({
  member_id: UUID("550e8400-e29b-41d4-a716-446655440000"),
  borrow_date: { $gte: ISODate("2024-04-01"), $lte: ISODate("2024-04-30") }
}).explain("executionStats")
```

---

## 3. Tạo Text Index và truy vấn

### 3.1 Tạo Text Index trên `book_title`
```js
db.loans.createIndex({ book_title: "text" })
```

### 3.2 Tìm kiếm văn bản có từ "Science Fiction"
```js
db.loans.find(
  { $text: { $search: ""Science Fiction"" } },
  { book_title: 1, score: { $meta: "textScore" } }
).sort({ score: { $meta: "textScore" } })
```

---

## 4. Tạo Unique Index

### 4.1 Tạo Unique Index trên `email`
```js
db.members.createIndex({ email: 1 }, { unique: true })
```

### 4.2 Chèn dữ liệu email trùng lặp thử lỗi
```js
db.members.insertOne({
  member_id: UUID("550e8400-e29b-41d4-a716-446655440099"),
  full_name: "Le Thi D",
  email: "nguyenb@example.com",
  joined_at: ISODate("2024-06-01")
})
```

---

## 5. Tạo TTL Index

### 5.1 Tạo TTL Index trên `created_at` trong `audit_logs` để tự động xóa sau 30 ngày
```js
db.audit_logs.createIndex(
  { created_at: 1 },
  { expireAfterSeconds: 2592000 }
)
```

### 5.2 Thêm một bản ghi log mới
```js
db.audit_logs.insertOne({
  log_id: UUID("8fa7b810-9dad-11d1-80b4-00c04fd430ff"),
  action: "BORROW",
  member_id: UUID("550e8400-e29b-41d4-a716-446655440000"),
  created_at: new Date()
})
```

---

## 6. Sử dụng Capped Collection

### 6.1 Tạo Capped Collection `system_notifications` dung lượng 1MB
```js
db.createCollection("system_notifications", {
  capped: true,
  size: 1048576
})
```

### 6.2 Thêm một thông báo mới
```js
db.system_notifications.insertOne({
  notification_id: UUID(),
  message: "System maintenance at 10PM",
  created_at: new Date()
})
```

---

## 7. Bulk Write Operations

```js
db.members.bulkWrite([
  { insertOne: { document: {
    member_id: UUID("550e8400-e29b-41d4-a716-446655440999"),
    full_name: "Tran Van C",
    email: "tran@example.com",
    joined_at: new Date()
  }}},
  { updateOne: {
    filter: { member_id: UUID("550e8400-e29b-41d4-a716-446655440000") },
    update: { $set: { email: "newemail@example.com" } }
  }},
  { deleteOne: {
    filter: { loan_id: UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8") }
  }},
  { insertOne: { document: {
    loan_id: UUID("aaa7b810-9dad-11d1-80b4-00c04fd43100"),
    member_id: UUID("550e8400-e29b-41d4-a716-446655440000"),
    book_id: UUID("bca7b810-9dad-11d1-80b4-00c04fd43100"),
    book_title: "MongoDB Basics",
    borrow_date: new Date(),
    due_date: new Date(Date.now() + 12096e5)
  }}},
  { insertOne: { document: {
    loan_id: UUID("bbb7b810-9dad-11d1-80b4-00c04fd43101"),
    member_id: UUID("550e8400-e29b-41d4-a716-446655440000"),
    book_id: UUID("cca7b810-9dad-11d1-80b4-00c04fd43101"),
    book_title: "Advanced NoSQL",
    borrow_date: new Date(),
    due_date: new Date(Date.now() + 12096e5)
  }}}
])
```

---

## 8. Kiểm tra và tối ưu hóa

### 8.1 Liệt kê tất cả chỉ mục trong `loans`
```js
db.loans.getIndexes()
```

### 8.2 So sánh hiệu suất truy vấn trên `loans` với `explain("executionStats")`
```js
db.loans.find({
  member_id: UUID("550e8400-e29b-41d4-a716-446655440000")
}).explain("executionStats")
```

### 8.3 Giám sát kích thước chỉ mục
```js
db.loans.stats()
```

---

# Giải thích tổng quan

- **Indexes** giúp tăng tốc truy vấn, tránh quét toàn bộ dữ liệu.
- **Compound Index** tối ưu truy vấn nhiều điều kiện cùng lúc.
- **Text Index** chuyên dùng cho tìm kiếm văn bản, nhanh hơn `$regex`.
- **Unique Index** đảm bảo dữ liệu không trùng lặp, giữ toàn vẹn hệ thống.
- **TTL Index** tự động xóa dữ liệu cũ, giúp quản lý dữ liệu tạm thời.
- **Capped Collection** lưu trữ dữ liệu vòng tròn, phù hợp log, thông báo.
- **Bulk Write** giảm số lần gửi truy vấn, tăng hiệu suất thao tác nhiều lệnh.
- **Explain()** cung cấp thông tin chi tiết về cách MongoDB thực thi truy vấn, giúp tối ưu chỉ mục.
- **Stats()** giúp giám sát kích thước bộ nhớ, tránh lãng phí tài nguyên.

---

