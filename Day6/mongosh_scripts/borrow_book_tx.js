//Giao dịch mượn sách (giảm stock, thêm loan)

const session = db.getMongo().startSession();
session.startTransaction({
  readConcern: { level: "snapshot" },
  writeConcern: { w: "majority", wtimeout: 5000 }
});

try {
  const booksColl = session.getDatabase("library").books;
  const loansColl = session.getDatabase("library").loans;

  const book = booksColl.findOne({ book_id: UUID("7ca7b810-9dad-11d1-80b4-00c04fd430c8") });

  if (book.stock > 0) {
    booksColl.updateOne(
      { book_id: book.book_id },
      { $inc: { stock: -1 } }
    );

    loansColl.insertOne({
      loan_id: UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8"),
      member_id: UUID("550e8400-e29b-41d4-a716-446655440000"),
      book_id: UUID("7ca7b810-9dad-11d1-80b4-00c04fd430c8"),
      borrow_date: ISODate("2024-04-01T00:00:00Z"),
      due_date: ISODate("2024-04-15T00:00:00Z"),
      status: "ACTIVE"
    });
  } else {
    throw new Error("Hết sách trong kho");
  }

  session.commitTransaction();
  print("Giao dịch mượn sách thành công.");
} catch (error) {
  print("Lỗi: " + error.message);
  session.abortTransaction();
} finally {
  session.endSession();
}
