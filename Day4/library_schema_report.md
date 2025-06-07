
# Thiết kế Schema và Quản lý Dữ liệu Quan hệ cho Hệ thống Thư viện Số

## 1. Bối cảnh
Hệ thống thư viện số sử dụng MongoDB để lưu trữ thông tin về:
- Thành viên (members)
- Sách (books)
- Lịch sử mượn trả (loans)

Yêu cầu thiết kế schema tối ưu, cân bằng hiệu suất và tính linh hoạt, hỗ trợ các mối quan hệ và xác thực dữ liệu.

---

## 2. Thiết kế Schema (Embedded vs Referenced Data)

### 2.1 Embedded Data (Nhúng dữ liệu)
Nhúng thông tin sách vào tài liệu loans:
```json
{
  loan_id: "L001",
  member_id: "M001",
  borrow_date: ISODate("2024-04-01T00:00:00Z"),
  books: [
    { title: "MongoDB Basics", author: "John Doe", category: "Database" },
    { title: "NoSQL Guide", author: "Jane Smith", category: "Tech" }
  ]
}
```

- **Ưu điểm:** Đọc nhanh hơn, không cần truy vấn bổ sung.
- **Nhược điểm:** Khó cập nhật nếu thông tin sách thay đổi.

### 2.2 Referenced Data (Tham chiếu)
Sử dụng khóa ngoại (ID) để tham chiếu:
```json
{
  loan_id: "L002",
  member_id: "M001",
  book_ids: ["B001", "B002"],
  borrow_date: ISODate("2024-04-01T00:00:00Z")
}
```

- **Ưu điểm:** Linh hoạt khi cập nhật dữ liệu.
- **Nhược điểm:** Cần truy vấn nhiều bảng để lấy thông tin.

### 2.3 Đề xuất:
- **Embedded:** Cho các trường hợp mượn ngắn hạn, thông tin sách ít thay đổi.
- **Referenced:** Khi cần cập nhật sách hoặc tồn kho thường xuyên.

---

## 3. Thiết kế Mối Quan Hệ

### One-to-One:
```json
{
  member_id: "M001",
  full_name: "Nguyen Van A",
  contact: {
    phone: "0912345678",
    address: "Yen Bai, Vietnam"
  }
}
```

### One-to-Many:
- Một thành viên có nhiều loans.

### Many-to-Many:
- Một sách có thể được mượn bởi nhiều thành viên và ngược lại.
- **Collection trung gian:** `loans`

### Truy vấn:
```js
db.loans.aggregate([
  { $match: { member_id: "M001" } },
  { $unwind: "$book_ids" },
  {
    $lookup: {
      from: "books",
      localField: "book_ids",
      foreignField: "book_id",
      as: "book_details"
    }
  },
  { $unwind: "$book_details" },
  { $project: { title: "$book_details.title", author: "$book_details.author" } }
])
```

---

## 4. Sử dụng DBRef

### Cấu trúc DBRef:
```json
{
  loan_id: UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8"),
  member: { $ref: "members", $id: UUID("550e8400-e29b-41d4-a716-446655440000") },
  book: { $ref: "books", $id: UUID("7ca7b810-9dad-11d1-80b4-00c04fd430c8") },
  borrow_date: ISODate("2024-04-01T00:00:00Z")
}
```

### Truy vấn:
```js
db.loans.findOne({ loan_id: UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8") })
// Sau đó cần truy vấn thủ công members và books theo $id.
```

### Nhược điểm của DBRef:
- Không tự động JOIN dữ liệu.
- Phải truy vấn thủ công.

---

## 5. Sử dụng Manual Referencing

### Schema:
```json
{
  loan_id: "L003",
  member_id: "M002",
  book_ids: ["B003", "B004"],
  borrow_date: ISODate("2024-04-01T00:00:00Z")
}
```

### Truy vấn bằng `$lookup`:
```js
db.loans.aggregate([
  { $match: { loan_id: "L003" } },
  {
    $lookup: {
      from: "members",
      localField: "member_id",
      foreignField: "member_id",
      as: "member_info"
    }
  },
  { $unwind: "$member_info" },
  { $unwind: "$book_ids" },
  {
    $lookup: {
      from: "books",
      localField: "book_ids",
      foreignField: "book_id",
      as: "book_info"
    }
  },
  { $unwind: "$book_info" },
  {
    $project: {
      loan_id: 1,
      member_name: "$member_info.full_name",
      book_title: "$book_info.title",
      borrow_date: 1
    }
  }
])
```

### So sánh Manual Referencing vs DBRef:
- Manual linh hoạt hơn, hỗ trợ `$lookup`
- DBRef không tự JOIN, ít dùng trong thực tế

---

## 6. So sánh với E-Commerce

### Ví dụ Schema:
```json
{
  order_id: UUID("..."),
  customer_id: UUID("..."),
  items: [
    { product_id: UUID("..."), name: "Laptop", price: 1000, quantity: 2 }
  ],
  total: 2000,
  order_date: ISODate("2024-04-01T00:00:00Z")
}
```

### So sánh:
| Đặc điểm        | Thư viện                       | E-commerce                     |
|----------------|--------------------------------|--------------------------------|
| Nhúng dữ liệu   | Liên hệ member (One-to-One)    | Sản phẩm trong đơn hàng        |
| Tham chiếu      | Sách trong loans               | Khách hàng trong order         |
| Quan hệ N-N     | Books – Members (via loans)    | Products – Orders (via items)  |

---

## 7. Validation: JSON Schema

### JSON Schema cho `members`:
```js
db.createCollection("members", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["full_name", "email", "joined_at"],
      properties: {
        full_name: { bsonType: "string", maxLength: 100 },
        email: { bsonType: "string", pattern: "^.+@.+$" },
        joined_at: { bsonType: "date" }
      }
    }
  }
})
```

### Thử chèn dữ liệu sai:
```js
db.members.insertOne({
  full_name: "Nguyen Van B",
  joined_at: new Date()
})
```
**Lỗi:** Document thiếu trường `email` → MongoDB trả lỗi validation.

### JSON Schema cho `books`:
```js
db.createCollection("books", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["title", "author", "stock"],
      properties: {
        title: { bsonType: "string" },
        author: { bsonType: "string" },
        stock: { bsonType: "int", minimum: 0 }
      }
    }
  }
})
```
