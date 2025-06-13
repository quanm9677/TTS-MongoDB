
# Tối Ưu Hệ Thống Đấu Giá Trực Tuyến với MongoDB

## I. Tổng Hợp Các Hoạt Động Tối Ưu Hóa

### 1. Truy Vấn Lịch Sử Đặt Giá (Query Optimization)

```javascript
db.bids.find({
  auction_id: UUID("550e8400-e29b-41d4-a716-446655440000"),
  bid_time: {
    $gte: ISODate("2024-06-01T10:00:00Z"),
    $lte: ISODate("2024-06-01T12:00:00Z")
  }
})
```

**Giải thích**: Nếu không có chỉ mục, MongoDB phải quét toàn bộ collection (COLLSCAN), làm giảm hiệu suất.

**Tối ưu bằng cách tạo chỉ mục:**

```javascript
db.bids.createIndex({ auction_id: 1, bid_time: 1 })
```

---

### 2. Covered Query

```javascript
db.bids.createIndex({ auction_id: 1, bid_time: 1, status: 1 })

db.bids.find(
  { auction_id: UUID("550e8400-e29b-41d4-a716-446655440000") },
  { auction_id: 1, bid_time: 1, status: 1, _id: 0 }
)
```

**Giải thích**: MongoDB không cần truy cập document gốc vì mọi dữ liệu đã có trong chỉ mục — giúp tăng tốc độ đáng kể.

---

### 3. Tránh Over-Indexing

**Sai lầm phổ biến**:

```javascript
// Tạo nhiều chỉ mục đơn lẻ
createIndex({ bidder_id: 1 })
createIndex({ bid_time: 1 })
createIndex({ status: 1 })
```

**Tối ưu**:

```javascript
db.bids.createIndex({ auction_id: 1, bid_time: 1, status: 1 })
```

**Giải thích**: Tạo quá nhiều chỉ mục riêng lẻ làm chậm ghi (write). Gộp chỉ mục theo truy vấn thực tế giúp tiết kiệm tài nguyên.

---

### 4. Phân Mảnh Dữ Liệu (Sharding)

```javascript
sh.enableSharding("auctiondb")
db.bids.createIndex({ auction_id: "hashed" })
sh.shardCollection("auctiondb.bids", { auction_id: "hashed" })
```

**Giải thích**: Giúp phân phối dữ liệu đều giữa các shard, tránh quá tải một node khi nhiều người dùng cùng truy cập một phiên đấu giá.

---

### 5. Replica Set và Đọc Phân Tán

```javascript
db.getMongo().setReadPref("primaryPreferred")
db.bids.find({ auction_id: UUID("550e8400-e29b-41d4-a716-446655440000") })
```

```javascript
db.getMongo().setReadPref("nearest")
db.auctions.find({})
```

**Giải thích**: Phù hợp với hệ thống toàn cầu, nơi cần giảm độ trễ truy vấn bằng cách đọc từ node gần nhất.

---

### 6. Aggregation Pipeline với Lọc Sớm (Early Filtering)

```javascript
db.bids.aggregate([
  {
    $match: {
      status: "ACCEPTED",
      bid_time: {
        $gte: ISODate("2024-06-01T00:00:00Z"),
        $lt: ISODate("2024-06-02T00:00:00Z")
      }
    }
  },
  {
    $group: {
      _id: "$auction_id",
      totalBidAmount: { $sum: "$bid_amount" }
    }
  },
  { $sort: { totalBidAmount: -1 } }
])
```

**Giải thích**: Đặt `$match` đầu pipeline giúp giảm số lượng document xử lý — tăng hiệu suất.

---

### 7. Kiểm Tra Hiệu Suất và Thống Kê

```javascript
db.runCommand({ collStats: "bids" })
```

**Giải thích**: Trả về kích thước dữ liệu, số document, và kích thước index.

```javascript
rs.status()
```

**Giải thích**: Kiểm tra trạng thái các node trong replica set (PRIMARY, SECONDARY).

```javascript
db.setProfilingLevel(1)
db.system.profile.find({ millis: { $gt: 100 } }).sort({ ts: -1 }).limit(5)
```

**Giải thích**: Theo dõi các truy vấn tốn trên 100ms để tối ưu tiếp.

---


