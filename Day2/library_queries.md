
# 📚 Quản Lý Thư Viện Số với MongoDB

## 1. 🏗️ Tạo Cơ Sở Dữ Liệu và Collection

```js
use digital_library  // Tạo và chuyển sang database

db.createCollection("members")
db.createCollection("loans")
```

---

## 2. 📥 Thêm Dữ Liệu Mẫu

### ➕ Collection: `members`
```js
db.members.insertMany([
  {
    member_id: UUID("550e8400-e29b-41d4-a716-446655440000"),
    full_name: "Nguyen Thi B",
    email: "nguyenb@example.com",
    contact: { phone: "0987654321", city: "Ho Chi Minh City" },
    interests: ["Fiction", "Science", "History"],
    joined_at: ISODate("2024-03-15T00:00:00Z")
  },
  {
    member_id: UUID("660e8400-e29b-41d4-a716-446655440000"),
    full_name: "Tran Van A",
    email: "vana@gmail.com",
    contact: { phone: "0911222333", city: "Hanoi" },
    interests: ["Technology", "Science"],
    joined_at: ISODate("2023-12-01T00:00:00Z")
  },
  {
    member_id: UUID("770e8400-e29b-41d4-a716-446655440000"),
    full_name: "Le Thi C",
    email: "lethi@example.com",
    contact: { phone: "0900112233", city: "Da Nang" },
    interests: ["Fiction", "History"],
    joined_at: ISODate("2024-05-20T00:00:00Z")
  }
])
```

### ➕ Collection: `loans`
```js
db.loans.insertMany([
  {
    loan_id: UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8"),
    member_id: UUID("550e8400-e29b-41d4-a716-446655440000"),
    books: [
      { book_id: UUID("7ca7b810-9dad-11d1-80b4-00c04fd430c8"), title: "Dune", borrow_date: ISODate("2024-04-01T00:00:00Z") },
      { book_id: UUID("8da7b810-9dad-11d1-80b4-00c04fd430c8"), title: "1984", borrow_date: ISODate("2024-04-01T00:00:00Z") }
    ],
    status: "ACTIVE",
    due_date: ISODate("2024-04-15T00:00:00Z")
  },
  {
    loan_id: UUID("9ba7b810-9dad-11d1-80b4-00c04fd430c9"),
    member_id: UUID("660e8400-e29b-41d4-a716-446655440000"),
    books: [
      { book_id: UUID("1fa7b810-9dad-11d1-80b4-00c04fd430c8"), title: "Brave New World", borrow_date: ISODate("2024-03-20T00:00:00Z") }
    ],
    status: "RETURNED",
    due_date: ISODate("2024-04-01T00:00:00Z")
  }
])
```

---

## 3. 🔍 Truy Vấn Dữ Liệu

### A. Logical Operators

```js
// $and: city = "Ho Chi Minh City" AND interests chứa "Fiction"
db.members.find({
  $and: [
    { "contact.city": "Ho Chi Minh City" },
    { interests: "Fiction" }
  ]
})

// $or: joined_at < 1/1/2024 OR email chứa "example.com"
db.members.find({
  $or: [
    { joined_at: { $lt: ISODate("2024-01-01T00:00:00Z") } },
    { email: /example\.com$/ }
  ]
})

// $not: loans không có status = "ACTIVE"
db.loans.find({
  status: { $not: { $eq: "ACTIVE" } }
})

// $nor: không có interests là "Science" và không ở "Hanoi"
db.members.find({
  $nor: [
    { interests: "Science" },
    { "contact.city": "Hanoi" }
  ]
})
```

### B. Element Operators

```js
// $exists: members có contact.phone
db.members.find({ "contact.phone": { $exists: true } })

// $type: loans có due_date là kiểu date
db.loans.find({ due_date: { $type: "date" } })
```

### C. Array Operators

```js
// $in: interests có bất kỳ ["Fiction", "History"]
db.members.find({ interests: { $in: ["Fiction", "History"] } })

// $nin: interests không chứa "Science" hoặc "Technology"
db.members.find({ interests: { $nin: ["Science", "Technology"] } })

// $all: interests chứa cả "Fiction" và "History"
db.members.find({ interests: { $all: ["Fiction", "History"] } })
```

### D. Sort

```js
// sort joined_at giảm dần
db.members.find().sort({ joined_at: -1 })

// sort loans theo due_date tăng dần và member_id giảm dần
db.loans.find().sort({ due_date: 1, member_id: -1 })
```

### E. Pagination

```js
// Lấy 10 thành viên đầu tiên, bỏ qua 20, sort full_name tăng dần
db.members.find().sort({ full_name: 1 }).skip(20).limit(10)

// Lấy 5 loans từ bản ghi thứ 11, sort due_date giảm dần
db.loans.find().sort({ due_date: -1 }).skip(10).limit(5)
```

### F. Projection

```js
// Chỉ trả về full_name và email, bỏ _id
db.members.find({}, { _id: 0, full_name: 1, email: 1 })

// Trả về member_id, status, books.title
db.loans.find({}, { _id: 0, member_id: 1, status: 1, "books.title": 1 })
```

### G. Embedded Documents

```js
// Tìm thành viên có city là "Hanoi"
db.members.find({ "contact.city": "Hanoi" })

// Tìm loans có ít nhất 1 sách borrow_date > 1/4/2024
db.loans.find({
  "books.borrow_date": { $gt: ISODate("2024-04-01T00:00:00Z") }
})
```

### H. Array Queries

```js
// Tìm members có đúng 3 interests
db.members.find({ interests: { $size: 3 } })

// Tìm loans có sách title = "Dune"
db.loans.find({ "books.title": "Dune" })
```
