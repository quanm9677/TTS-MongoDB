//Demo writeConcern và wtimeout

db.loans.insertOne(
  {
    loan_id: UUID(),
    member_id: UUID("550e8400-e29b-41d4-a716-446655440000"),
    book_id: UUID("7ca7b810-9dad-11d1-80b4-00c04fd430c8"),
    borrow_date: new Date(),
    due_date: new Date(Date.now() + 14 * 86400000),
    status: "ACTIVE"
  },
  { writeConcern: { w: "majority", wtimeout: 3000 } }
);
