
# 📊 Phân tích Dữ liệu Thư viện với Aggregation Pipeline MongoDB


---

## **1. Dữ liệu mẫu**

### **Collection: members**
```json
{
  "member_id": UUID("550e8400-e29b-41d4-a716-446655440000"),
  "full_name": "Nguyen Thi B",
  "email": "nguyenb@example.com",
  "joined_at": ISODate("2024-03-15T00:00:00Z")
}
```

### **Collection: loans**
```json
{
  "loan_id": UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8"),
  "member_id": UUID("550e8400-e29b-41d4-a716-446655440000"),
  "books": [
    {
      "book_id": UUID("7ca7b810-9dad-11d1-80b4-00c04fd430c8"),
      "title": "Dune",
      "borrow_date": ISODate("2024-04-01T00:00:00Z")
    },
    {
      "book_id": UUID("8da7b810-9dad-11d1-80b4-00c04fd430c8"),
      "title": "1984",
      "borrow_date": ISODate("2024-04-02T00:00:00Z")
    }
  ],
  "due_date": ISODate("2024-04-15T00:00:00Z"),
  "status": "ACTIVE"
}
```

---

## **2. Yêu cầu và Pipeline**

### `$match`
#### a) Lọc giao dịch mượn trong tháng 4/2024:
```js
db.loans.aggregate([
  {
    $match: {
      status: "ACTIVE",
      due_date: {
        $gte: ISODate("2024-04-01T00:00:00Z"),
        $lt: ISODate("2024-05-01T00:00:00Z")
      }
    }
  }
])
```
#### b) Thành viên đăng ký sau 01/01/2024:
```js
db.members.aggregate([
  {
    $match: {
      joined_at: { $gt: ISODate("2024-01-01T00:00:00Z") }
    }
  }
])
```

### `$group`
#### a) Số lượt mượn theo `member_id`:
```js
db.loans.aggregate([
  {
    $group: {
      _id: "$member_id",
      total_loans: { $sum: 1 }
    }
  }
])
```
#### b) Số lượt mượn theo `books.book_id`:
```js
db.loans.aggregate([
  { $unwind: "$books" },
  {
    $group: {
      _id: "$books.book_id",
      total_borrowed: { $sum: 1 }
    }
  }
])
```

### `$sort`
#### a) Thành viên mượn nhiều nhất:
```js
db.loans.aggregate([
  {
    $group: {
      _id: "$member_id",
      total_loans: { $sum: 1 }
    }
  },
  { $sort: { total_loans: -1 } }
])
```
#### b) Sách mượn ít nhất:
```js
db.loans.aggregate([
  { $unwind: "$books" },
  {
    $group: {
      _id: "$books.title",
      borrow_count: { $sum: 1 }
    }
  },
  { $sort: { borrow_count: 1 } }
])
```

### `$project`
#### a) Hiển thị tên viết hoa và năm đăng ký:
```js
db.members.aggregate([
  {
    $project: {
      _id: 0,
      full_name: { $toUpper: "$full_name" },
      email: 1,
      year_joined: { $year: "$joined_at" }
    }
  }
])
```
#### b) Thêm trường số lượng sách:
```js
db.loans.aggregate([
  {
    $project: {
      loan_id: 1,
      status: 1,
      total_books: { $size: "$books" }
    }
  }
])
```

### `$unwind`
```js
db.loans.aggregate([
  { $unwind: "$books" }
])
```

### `$limit` và `$skip`
#### a) Top 5 thành viên mượn nhiều:
```js
db.loans.aggregate([
  {
    $group: {
      _id: "$member_id",
      total_loans: { $sum: 1 }
    }
  },
  { $sort: { total_loans: -1 } },
  { $limit: 5 }
])
```
#### b) Lấy 10 bản ghi từ thứ 11:
```js
db.loans.aggregate([
  { $sort: { due_date: -1 } },
  { $skip: 10 },
  { $limit: 10 }
])
```

### Thống kê tổng hợp
#### a) Đếm giao dịch ACTIVE:
```js
db.loans.aggregate([
  { $match: { status: "ACTIVE" } },
  { $count: "active_loans" }
])
```
#### b) Tổng sách đã mượn:
```js
db.loans.aggregate([
  {
    $group: {
      _id: null,
      total_books_borrowed: { $sum: { $size: "$books" } }
    }
  }
])
```
#### c) Trung bình sách/giao dịch:
```js
db.loans.aggregate([
  {
    $group: {
      _id: null,
      avg_books: { $avg: { $size: "$books" } }
    }
  }
])
```
#### d) Ngày mượn đầu/cuối:
```js
db.loans.aggregate([
  { $unwind: "$books" },
  {
    $group: {
      _id: null,
      earliest_borrow: { $min: "$books.borrow_date" },
      latest_borrow: { $max: "$books.borrow_date" }
    }
  }
])
```

### Pipeline phức tạp theo danh mục:
```js
db.loans.aggregate([
  { $unwind: "$books" },
  { $match: { "books.category": { $exists: true } } },
  {
    $group: {
      _id: "$books.category",
      total_borrowed: { $sum: 1 }
    }
  },
  { $sort: { total_borrowed: -1 } }
])
```

### `$cond` xác định quá hạn:
```js
db.loans.aggregate([
  {
    $project: {
      loan_id: 1,
      due_date: 1,
      is_overdue: {
        $cond: { if: { $lt: ["$due_date", "$$NOW"] }, then: true, else: false }
      }
    }
  }
])
```

---

## **So sánh Aggregation Pipeline vs MapReduce**

| Tiêu chí | Aggregation Pipeline | MapReduce |
|---------|----------------------|-----------|
| Cú pháp | Ngắn gọn, trực quan  | Dài, phức tạp |
| Hiệu năng | Cao hơn do tối ưu hóa | Thấp hơn |
| Linh hoạt | Tốt trong trường hợp phổ biến | Tùy biến sâu (dùng JS) |
| Ứng dụng | Phân tích, thống kê, báo cáo | Tính toán đặc thù phức tạp |
