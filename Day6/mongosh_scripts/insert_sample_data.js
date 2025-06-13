// Khởi tạo dữ liệu mẫu (books, members)

// use library;

db.members.insertOne({
  member_id: UUID("550e8400-e29b-41d4-a716-446655440000"),
  full_name: "Nguyen Thi B",
  email: "nguyenb@example.com",
  joined_at: ISODate("2024-03-15T00:00:00Z")
});

db.books.insertOne({
  book_id: UUID("7ca7b810-9dad-11d1-80b4-00c04fd430c8"),
  title: "Dune",
  author: "Frank Herbert",
  stock: 5
});
