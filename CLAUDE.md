# Quy ước đặt tên file — `prompts/` và `artifacts/reports/`

Áp dụng cho **file mới** tạo trong hai thư mục này từ nay về sau. Không bắt buộc đổi tên các
file lịch sử đã tồn tại (xem mục "Ngoại lệ" bên dưới).

## Chuẩn đặt tên bắt buộc cho file mới

```
yy-mm-dd-hh-mm-ten-tinh-nang.md
```

- `yy-mm-dd` — năm 2 chữ số, tháng, ngày (giờ hệ thống local, không phải UTC).
- `hh-mm` — giờ:phút lúc tạo file, 24h, luôn 2 chữ số.
- `ten-tinh-nang` — mô tả ngắn tính năng/nội dung, **viết thường, gạch ngang, không dấu,
  không khoảng trắng, không ký tự đặc biệt**.

Ví dụ hợp lệ:

```
26-09-14-07-30-docker-production-audit.md
26-09-14-14-05-algorithm-v3-momentum-tuning.md
26-09-15-09-00-security-review-http-allowlist.md
```

Ví dụ **không** hợp lệ:

```
DockerAudit.md                 # thiếu timestamp, dùng chữ hoa
2026_09_14_docker.md           # sai định dạng dấu phân cách, thiếu giờ:phút
26-09-14-docker production.md  # có khoảng trắng, không có giờ:phút
```

## Lý do

- **Sort theo thời gian tự nhiên**: tên file bắt đầu bằng timestamp nên `ls`/file explorer
  sắp xếp đúng thứ tự thời gian mà không cần đọc nội dung.
- **Truy vết theo phiên làm việc**: mỗi file map 1-1 với một phiên audit/nghiên cứu/nâng cấp
  cụ thể — biết ngay file nào sinh ra từ đợt làm việc nào mà không cần mở `git log`.
- **Tránh trùng tên / ghi đè nhầm**: hai phiên làm việc khác nhau trong cùng ngày vẫn có tên
  file khác nhau nhờ giờ:phút.

## Ngoại lệ — file "living document" giữ nguyên tên cố định

Các file sau đóng vai trò tài liệu **sống** (living document) — được **cập nhật tại chỗ**
qua nhiều phiên làm việc, không phải file chụp nhanh một lần rồi giữ nguyên. Vì vậy chúng
**không** theo mẫu timestamp và **không được đổi tên**:

| File | Vai trò |
| --- | --- |
| `artifacts/reports/FINAL_VERDICT.md` | Kết luận khoa học + kỹ thuật mới nhất — luôn ghi đè, không tạo bản mới mỗi lần |
| `artifacts/reports/BASELINE_AUDIT.md` | Baseline audit gốc trước khi sửa — có thể cập nhật khi baseline thay đổi |
| `artifacts/reports/BROWSER_ACCEPTANCE.md` | Báo cáo chấp nhận browser E2E hiện hành |
| `artifacts/reports/ALGORITHM_V2_RESEARCH.md` | Sổ tay nghiên cứu thuật toán hiện hành |
| `artifacts/reports/PROVENANCE_AUDIT.md` | Kết quả audit provenance hiện hành |
| `artifacts/reports/PRODUCTION_SCORECARD.md` | Bảng điểm production hiện hành |
| `artifacts/reports/DOCKER_SMOKE.md` | Kết quả smoke test Docker gần nhất |

Nếu một báo cáo trong danh sách trên cần được **thay thế hoàn toàn** (không phải cập nhật)
bởi một đợt audit mới với phạm vi khác hẳn, hãy đặt tên bản audit mới theo chuẩn timestamp
(vd. `26-10-01-15-20-algorithm-v3-full-reaudit.md`) và giữ nguyên file cũ làm lịch sử, thay vì
ghi đè trực tiếp lên file "living document" đang có.

## Áp dụng cho `prompts/`

Mọi master-prompt mới thêm vào `prompts/` (dùng để chỉ đạo một đợt audit/nâng cấp/nghiên cứu
cụ thể) phải theo chuẩn timestamp ở trên. Hai file hiện có trong thư mục này được tạo trước
khi có quy ước này nên giữ nguyên tên gốc:

- `MASTER PROMPT — Greenfield Vietlott Python + Streamlit Quant Research Lab.md`
- `MASTER PROMPT — Browser-Verified Production Audit & Algorithm Upgrade for Vietlott Quant Research Lab.md`

## Áp dụng cho `artifacts/reports/`

File báo cáo mới **không** thuộc danh sách "living document" ở trên (vd. một báo cáo audit
bảo mật đột xuất, một báo cáo thử nghiệm thuật toán một lần, một báo cáo sự cố) phải theo
chuẩn timestamp. `browser_screenshots/` và `streamlit_server.log` là output tạm sinh ra khi
chạy test/audit, không thuộc phạm vi quy ước đặt tên này.
