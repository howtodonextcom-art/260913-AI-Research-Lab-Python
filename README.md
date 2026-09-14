# Vietlott Quant Research Lab

**Dự án này KHÔNG dự đoán kết quả xổ số.**

Đây là một **phòng thí nghiệm nghiên cứu định lượng (quantitative research lab)** cho xổ số
Mega 6/45 của Vietlott: thu thập lịch sử quay thưởng chính thức, tính đặc trưng (feature)
không rò rỉ thông tin tương lai, xếp hạng 01–45, tạo pool ứng viên lồng nhau (18→7), so sánh
với mô hình null chính xác (exact hypergeometric), chạy giải đấu (tournament) giữa các mô
hình theo protocol Development/Validation/Test, và đóng băng (freeze) dự đoán trước khi kỳ
quay diễn ra để chấm điểm minh bạch sau này (prospective scoring).

Mẫu hình lịch sử được coi là **giả thuyết cần kiểm định**, không phải dự báo. Một kết quả
khoa học hợp lệ — và là kết quả hiện tại của dự án — là:

```text
NO_RANKING_EDGE_FOUND
```

nghĩa là: chưa có bằng chứng đủ mạnh, đã qua kiểm định holdout/temporal, cho thấy bất kỳ
phương pháp xếp hạng nào đặt 6 số trúng thưởng của một kỳ quay tương lai vào vị trí tốt hơn
một cách hệ thống so với xếp hạng ngẫu nhiên hoàn toàn.

`RANKING SCORE ≠ PROBABILITY`. `Evidence khoa học` và `Production readiness` là hai trục
đánh giá **độc lập** — một hệ thống có thể vận hành ổn định về kỹ thuật (`PRODUCTION_READY`)
trong khi kết luận khoa học vẫn là `NO_RANKING_EDGE_FOUND`. Không có mâu thuẫn nào ở đây.

Nguồn dữ liệu chính thức duy nhất cho môi trường production: **vietlott.vn**. Không dùng
GitHub/Kaggle mirror làm dữ liệu production.

## Trạng thái hiện tại

Theo `artifacts/reports/FINAL_VERDICT.md` (cập nhật sau đợt audit P0–P10 + Docker closeout):

| Trục đánh giá | Kết luận |
| --- | --- |
| Khoa học (scientific verdict) | `NO_RANKING_EDGE_FOUND` |
| Kỹ thuật (production verdict) | `PRODUCTION_READY` |

Dataset: 1562 kỳ quay, kỳ mới nhất `#01562` (2026-09-13). Xem chi tiết đầy đủ (bảng
metric Dev/Validation/Test, các mô hình đã thử, rủi ro chưa xử lý) trong
`artifacts/reports/FINAL_VERDICT.md` và `ALGORITHM_V2_RESEARCH.md`.

## Kiến trúc / luồng dữ liệu

```text
vietlott.vn (official)
  → httpx (allowlist host + rate limit + timeout)
  → raw snapshot (immutable audit marker)
  → parser (regex chính + BeautifulSoup dự phòng) + schema guard
  → Parquet canonical (data/processed/) + manifest/DuckDB (data/manifests/)
  → Feature vector 01–45 tại mốc t, chỉ dùng draws < t (leak-safe)
  → Ranking 01–45 (nhiều model — xem bảng dưới)
  → Nested Top-m pool (18 → 7)
  → So sánh với null hypergeometric chính xác
  → Window tournament → Model tournament (Dev/Validation/Test)
  → Pool-18 gate → Compression frontier
  → Prospective freeze (hash chain append-only) → score sau khi có kết quả thật
  → Streamlit UI chỉ đọc service/artifact — không chứa logic nghiên cứu
```

### Các họ mô hình xếp hạng đã triển khai (`src/vietlott_quant_lab/ranking/models/`)

| Model ID | Ý tưởng |
| --- | --- |
| `hot` | Tần suất trong một cửa sổ lookback (baseline Round 1) |
| `multi_scale_shrinkage` | Nhiều cửa sổ + gap + momentum + stability + shrinkage, trọng số thủ công (baseline Round 1) |
| `random` | Hoán vị ngẫu nhiên có seed — đối chứng null |
| `all_history` | Tần suất toàn bộ lịch sử |
| `ewf` | Exponentially-weighted frequency, nửa chu kỳ (half-life) chọn qua Development |
| `multi_scale_v2` | Bản nâng cấp của multi-scale, trọng số chọn qua Development/Validation thay vì gán tay |
| `momentum` | Giả thuyết tiếp diễn (continuation) |
| `mean_reversion` | Giả thuyết đảo chiều (đối trọng của momentum) |
| `hazard` | Đặc trưng thời gian chờ thực nghiệm (waiting-time), không gọi số "đến hạn" |
| `reverse_peek`, `shuffled_history` | Đối chứng cố ý sai (control) — dùng để kiểm tra bộ khung thống kê có tự phát hiện tín hiệu giả hay không |

Model không được coi là "vô địch" chỉ vì phức tạp hơn — mọi promotion đều phải qua
Development → Validation → xác nhận Test một lần duy nhất (không tinh chỉnh lại sau khi xem
Test).

### Thống kê & kiểm định (`src/vietlott_quant_lab/statistics/`)

- `hypergeometric.py` — null model chính xác (không Monte Carlo) cho P(K=k) theo kích thước
  pool.
- `inference.py` — Newey-West HAC, moving-block bootstrap, paired permutation, ngoài
  Student-t đơn thuần (vì các draw có phụ thuộc chuỗi do cửa sổ lookback chồng lấp).
- `multiplicity.py` — hiệu chỉnh Holm-Bonferroni cho họ kiểm định nhiều mô hình/cửa sổ.
- `metrics.py` — Mean K, P(K≥4)/P(K≥5)/P(K=6), Mean/Median winner rank, MCP (Maximum
  Contained Position).

### Nghiên cứu (`src/vietlott_quant_lab/research/`)

`split.py` (chia thời gian Dev/Validation/Test, không xáo trộn) · `window_tournament.py` ·
`model_tournament.py` / `model_tournament_v2.py` · `pool_gate.py` (gate 45→18) ·
`compression.py` (đường cong nén 18→7) · `ablation.py` (loại bỏ từng thành phần đặc trưng,
gán nhãn `HELPFUL`/`NEUTRAL`/`HARMFUL`, và bộ kiểm tra độ bở — fragility battery) ·
`protocol.py` / `protocol_v2.py` (đăng ký protocol dạng hash, chống thay đổi tiêu chí sau khi
đã thấy kết quả) · `verdict.py` (tính verdict khoa học từ artifact thật, không gán tay).

### Prospective (`src/vietlott_quant_lab/prospective/`)

Đóng băng (freeze) xếp hạng 01–45 và pool 18→7 **trước** khi biết kết quả kỳ quay tiếp theo,
lưu vào chuỗi hash nối tiếp (append-only hash chain, `artifacts/prospective/freezes.jsonl`).
Sau khi có kết quả thật, chỉ được phép **append** điểm số — không bao giờ ghi đè bản ghi cũ.

### Data integrity (`src/vietlott_quant_lab/data/`)

Fail-closed theo thiết kế: trang lịch sử rỗng/bất thường chỉ được coi là hết dữ liệu nếu đã
xác nhận thấy kỳ neo (`#00001` hoặc kỳ đã đồng bộ gần nhất); nếu không, hệ thống báo lỗi
`SOURCE_SCHEMA_CHANGED` thay vì âm thầm trả về dataset rỗng. **Lưu ý về giới hạn hiện tại:**
snapshot trong `data/raw/` hiện chỉ là một chuỗi đánh dấu nhẹ (`sync:{mode}:fetched={count}`),
**không phải** toàn bộ nội dung HTML/AjaxPro đã tải — xem `docs/data-source.md` và
`artifacts/reports/BASELINE_AUDIT.md` để biết chi tiết khoảng trống này.

## Giao diện Streamlit (`pages/`)

UI chỉ đọc artifact/service cục bộ, không tự ý gọi mạng mỗi lần rerun.

| Trang | Nội dung |
| --- | --- |
| `01_overview.py` | Verdict khoa học + kỹ thuật, dataset, evidence level |
| `02_data_library.py` | Bảng lịch sử kỳ quay, lọc, kiểm tra integrity |
| `03_number_lab.py` | Đặc trưng của từng số 01–45, đổi model để so sánh xếp hạng |
| `04_candidate_pool.py` | Pool 18→7, Mean K so với null, P4/P5/P6, MCP, số vé Bao, chi phí |
| `05_ab_tournament.py` | Kết quả tournament Dev/Validation/Test theo model |
| `06_compression_frontier.py` | Đường cong nén pool 18→7 (containment, chi phí) |
| `07_prospective.py` | Trạng thái chuỗi hash, freeze đang chờ/đã chấm điểm |
| `08_system_health.py` | Tình trạng nguồn dữ liệu, DuckDB, artifact, chuỗi prospective |

Nội dung raw JSON/debug được gom vào khối "Advanced / Debug" thay vì hiển thị làm nội dung
chính, để tránh gây hiểu nhầm là "kết quả chính thức".

## Yêu cầu môi trường

- Python **>= 3.12**
- Khuyến nghị dùng virtual environment
- Docker (tùy chọn, xem phần Docker bên dưới)

## Cài đặt

```bash
python -m venv .venv
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate

pip install -e ".[dev]"
```

Sao chép file env mẫu nếu cần:

```bash
copy .env.example .env
```

## Chạy giao diện Streamlit

```bash
streamlit run app.py
```

Tương đương CLI để đồng bộ dữ liệu chính thức:

```bash
python -m scripts.sync_official
```

## Test và CI

```bash
pytest -q                    # unit/integration (85 test hiện tại), không chạm mạng
pytest tests/browser -q      # E2E trình duyệt thật (Playwright + Chromium), tách riêng
ruff check src tests scripts app.py pages
mypy src/vietlott_quant_lab  # strict, blocking trong CI
```

GitHub Actions (`.github/workflows/`):

- **`ci.yml`** — job `test` (ruff, mypy strict blocking, pytest) rồi job `browser-e2e`
  (cài Chromium, chạy `tests/browser` với server Streamlit cục bộ, upload screenshot khi
  fail). Không job nào dùng `continue-on-error` cho gate bắt buộc.
- **`live-source-check.yml`** — chạy thủ công hoặc theo lịch, kiểm tra vietlott.vn read-only,
  không bao giờ dùng để ghi dữ liệu canonical.

## Docker

```bash
docker build -t vietlott-quant-lab .
docker run --rm -p 8501:8501 vietlott-quant-lab
```

Xem `docs/deployment.md` và `artifacts/reports/DOCKER_SMOKE.md` (kết quả smoke test thật,
không chỉ dựa vào cú pháp Dockerfile).

## Nghiên cứu qua CLI

Các tác vụ chạy lâu nằm ở `scripts/`, không chạy trực tiếp trong UI:

```bash
python -m scripts.sync_official              # đồng bộ tăng dần
python -m scripts.sync_official --force      # crawl toàn bộ về #00001
python -m scripts.run_window_tournament
python -m scripts.run_model_tournament --no-window-selection
python -m scripts.run_algorithm_v2           # tournament Algorithm V2 (EWF, multi_scale_v2, momentum, mean_reversion, hazard...)
python -m scripts.generate_v2_report         # sinh artifacts/reports/ALGORITHM_V2_RESEARCH.md
python -m scripts.freeze_prospective --model hot
python -m scripts.score_prospective
python -m scripts.live_source_check          # kiểm tra khả dụng nguồn, read-only
```

## Tài liệu

- [Kiến trúc](docs/architecture.md)
- [Nguồn dữ liệu](docs/data-source.md)
- [Protocol nghiên cứu](docs/research-protocol.md)
- [Null thống kê](docs/statistical-null.md)
- [Prospective](docs/prospective.md)
- [Triển khai](docs/deployment.md)
- [Runbook](docs/runbook.md)
- [Quy ước đặt tên file `prompts/` và `artifacts/reports/`](CLAUDE.md)

Báo cáo kết luận cuối: `artifacts/reports/FINAL_VERDICT.md`.

## Cấu trúc thư mục

```text
app.py                                  # entrypoint Streamlit
pages/01_overview.py … 08_system_health.py
src/vietlott_quant_lab/
  config/        # settings (env-backed), hằng số sản phẩm
  data/          # crawl, parse, lưu trữ canonical, kiểm tra integrity (fail-closed)
  features/      # đặc trưng leak-safe tại mốc thời gian t
  ranking/       # engine + các model xếp hạng 01–45, nested pool
  research/      # protocol, tournament, gate, ablation, artifact thí nghiệm
  statistics/    # null hypergeometric, HAC/bootstrap/permutation, multiplicity, metrics
  prospective/   # freeze/score dạng hash chain append-only
  optimization/  # tổ hợp Bao (vé, chi phí)
  provenance/    # hàm hash canonical dùng chung
  observability/ # logging có cấu trúc
  ui/            # cache/chart/label/loader — chỉ đọc, không chứa logic nghiên cứu
data/{raw,processed,snapshots,manifests}
artifacts/{experiments,prospective,reports}
tests/           # unit/integration (mặc định) + tests/browser (E2E, tách riêng)
scripts/         # CLI cho tác vụ chạy lâu (sync, tournament, freeze, report)
prompts/         # master-prompt dùng để chỉ đạo các đợt audit/nâng cấp — xem CLAUDE.md
docs/            # tài liệu kiến trúc, protocol, vận hành
.github/workflows/
```
