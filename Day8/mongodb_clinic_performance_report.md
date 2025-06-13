
# 📊 Báo cáo: Tối ưu hóa hiệu suất hệ thống quản lý phòng khám y tế với MongoDB

## 🩺 Bối cảnh
Bạn là nhà phát triển cơ sở dữ liệu cho hệ thống quản lý phòng khám y tế, sử dụng MongoDB để lưu trữ thông tin bệnh nhân, lịch hẹn, và hồ sơ y tế. Hệ thống cần xử lý lượng lớn truy vấn từ bác sĩ, nhân viên và bệnh nhân. Nhiệm vụ của bạn là đảm bảo hiệu suất cao, tối ưu hóa lưu trữ và quản lý tài nguyên hiệu quả.

---

## 1. 🧱 Index Maintenance (Tái tạo chỉ mục và Compact)

### 🔁 ReIndex collection `appointments`
```js
// Chạy trong mongosh (nếu không được hỗ trợ trực tiếp, export/import là cách thay thế)
db.appointments.reIndex();
```

### 📦 Compact collection `medical_records`
```js
db.runCommand({ compact: "medical_records" });
```

### 📏 Giám sát chỉ mục bằng collStats
```js
db.appointments.stats();
db.medical_records.stats();
```

---

## 2. 💾 Storage Optimization với WiredTiger Engine

### ⚙️ Cấu hình cache size (chạy khi khởi động mongod)
```bash
mongod --wiredTigerCacheSizeGB 2
```

### 📘 WiredTiger sử dụng B-tree (mặc định) và hỗ trợ LSM (ít dùng trong MongoDB). B-tree phù hợp cho:
- Truy cập ngẫu nhiên (random reads)
- Thêm/sửa nhanh
- Đọc theo chỉ mục hiệu quả

### 📊 Giám sát hiệu suất lưu trữ:
```js
db.serverStatus().wiredTiger.cache["cache pages requested from the cache"];
db.serverStatus().wiredTiger.cache["unmodified pages evicted"];
```

---

## 3. 📦 Compression (nén dữ liệu)

### medical_records sử dụng `zlib`:
```js
db.createCollection("medical_records", {
  storageEngine: {
    wiredTiger: {
      configString: "block_compressor=zlib"
    }
  }
});
```

### appointments sử dụng `snappy`:
```js
db.createCollection("appointments", {
  storageEngine: {
    wiredTiger: {
      configString: "block_compressor=snappy"
    }
  }
});
```

### So sánh:
| Thuộc tính   | zlib (medical_records)     | snappy (appointments)        |
|--------------|----------------------------|-------------------------------|
| Tỷ lệ nén    | Cao                        | Trung bình                    |
| Hiệu suất    | Tốc độ chậm hơn            | Nhanh hơn                     |
| CPU          | Tốn nhiều hơn              | Nhẹ                          |
| Phù hợp      | Ghi chú dài, văn bản lớn   | Truy vấn thường xuyên        |

---

## 4. 🕵️‍♂️ Profiling và Truy vấn chậm

### Bật profiler:
```js
db.setProfilingLevel(1, { slowms: 100 });
```

### Truy vấn tìm các truy vấn chậm:
```js
db.system.profile.find({
  ns: "clinic.appointments",
  millis: { $gt: 100 }
}).sort({ ts: -1 }).limit(5);
```

### Đề xuất cải tiến: Thêm chỉ mục kết hợp
```js
db.appointments.createIndex({ patient_id: 1, appointment_date: 1 });
```

---

## 5. 🧠 In-Memory Caching

### Truy vấn tận dụng cache:
```js
const today = new Date();
today.setHours(0,0,0,0);
const tomorrow = new Date(today);
tomorrow.setDate(tomorrow.getDate() + 1);

db.appointments.find({
  appointment_date: { $gte: today, $lt: tomorrow }
});
```

### Tăng kích thước cache (khi khởi động mongod):
```bash
mongod --wiredTigerCacheSizeGB 2
```

---

## 6. 🚀 Bulk Operations

### 1. Thêm 100 bệnh nhân:
```js
let bulkPatients = [];
for (let i = 0; i < 100; i++) {
  bulkPatients.push({
    insertOne: {
      document: {
        patient_id: UUID(),
        full_name: `Patient ${i}`,
        email: `patient${i}@example.com`,
        phone: `01234567${i}`,
        registered_at: new Date()
      }
    }
  });
}
db.patients.bulkWrite(bulkPatients, { ordered: false });
```

### 2. Cập nhật 50 lịch hẹn:
```js
async function runBulkUpdate() {
  let bulkUpdates = [];
  let idsToUpdate = await db.appointments.find({ status: "SCHEDULED" }).limit(50).toArray();
  idsToUpdate.forEach(doc => {
    bulkUpdates.push({
      updateOne: {
        filter: { _id: doc._id },
        update: { $set: { status: "COMPLETED" } }
      }
    });
  });
  if (bulkUpdates.length > 0) {
    const result = await db.appointments.bulkWrite(bulkUpdates, { ordered: false });
    printjson(result);
  }
}
runBulkUpdate();
```

### 3. Thêm 200 hồ sơ y tế:
```js
let bulkRecords = [];
for (let i = 0; i < 200; i++) {
  bulkRecords.push({
    insertOne: {
      document: {
        record_id: UUID(),
        patient_id: UUID(),
        visit_date: new Date(),
        symptoms: ["cough"],
        prescription: "Vitamin C",
        notes: "Check again"
      }
    }
  });
}
db.medical_records.bulkWrite(bulkRecords, { ordered: false });
```

---

## 7. 🧩 Schema Optimization với Denormalization

### Ví dụ nhúng thông tin bệnh nhân:
```js
{
  appointment_id: UUID("..."),
  patient: {
    patient_id: UUID("..."),
    full_name: "Nguyen Van A",
    email: "nguyen@example.com"
  },
  doctor_id: UUID("..."),
  appointment_date: ISODate("2024-06-01T09:00:00Z"),
  status: "SCHEDULED"
}
```

### So sánh:

| Tiêu chí                 | Denormalization                      | Normalization                     |
|--------------------------|--------------------------------------|-----------------------------------|
| Truy vấn nhanh           | ✅ Không cần join                    | ❌ Cần `$lookup`                  |
| Cập nhật thông tin bệnh nhân | ❌ Phức tạp nếu thay đổi           | ✅ Dễ dàng cập nhật               |
| Kích thước dữ liệu       | 📈 Tăng do trùng lặp                 | 📉 Nhỏ gọn                        |
| Tính nhất quán           | ❌ Dễ lỗi nếu không update đồng bộ   | ✅ Luôn đúng                      |

### Gợi ý:
- Dùng nhúng khi tạo **báo cáo lịch hẹn hàng ngày**, **in lịch hẹn**, **giao diện lịch**.
- Dùng tham chiếu khi cần **cập nhật bệnh nhân**, liên kết tới nhiều bảng.

---

## 8. 🔍 Kiểm tra và giám sát hiệu suất

### Kiểm tra kích thước dữ liệu và chỉ mục:
```js
db.medical_records.stats();
```

### Giám sát I/O bằng `mongostat` (chạy trên terminal):
```bash
mongostat --host localhost --port 27017
```

### Giám sát hoạt động đọc/ghi bằng `mongotop`:
```bash
mongotop 5
```

### Định kỳ kiểm tra index/dữ liệu:
```js
db.appointments.stats();
db.medical_records.stats();
```

---


