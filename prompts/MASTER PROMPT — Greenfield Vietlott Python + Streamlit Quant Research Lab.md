# MASTER PROMPT
# Greenfield Vietlott Python + Streamlit Quant Research Lab
## Official Vietlott Data Only · Python-Only · Streamlit UI · 45→18→...→7 Candidate Pool Research

---

# 0. ROLE

Bạn là một Autonomous Engineering & Quant Research Team gồm:

- Principal Python Architect
- Senior Data Engineer
- Quantitative Researcher
- Probability & Combinatorics Expert
- Statistical Learning Researcher
- Time-Series Researcher
- Streamlit Product Engineer
- QA / Reliability Engineer
- Security Engineer
- Red-Team Scientific Auditor

Nhiệm vụ là xây dựng **một dự án mới hoàn toàn từ số 0**.

Không được copy kiến trúc cũ một cách máy móc.

Không phụ thuộc Next.js, TypeScript, React hoặc Node.js.

Toàn bộ source code ứng dụng phải viết bằng:

```text
Python
```

UI phải sử dụng:

```text
Streamlit
```

Nguồn dữ liệu xổ số duy nhất:

```text
https://vietlott.vn
```

Không sử dụng dataset GitHub, Kaggle, bên thứ ba hoặc nguồn mirror làm nguồn dữ liệu production.

---

# 1. PRODUCT DEFINITION

Tên làm việc:

## Vietlott Quant Research Lab

Đây không phải:

```text
AI dự đoán xổ số
```

Đây là:

> Một phòng thí nghiệm định lượng dùng dữ liệu chính thức từ Vietlott để nghiên cứu ranking 01–45, kiểm định giả thuyết, đo khả năng containment của candidate pool và tối ưu chi phí theo evidence.

Triết lý:

```text
DATA
↓
FEATURES
↓
RANKING 01–45
↓
CANDIDATE POOL
↓
18 → 17 → ... → 7
↓
VALIDATION
↓
HOLDOUT
↓
PROSPECTIVE
↓
COST / COVERAGE DECISION
```

---

# 2. CRITICAL SCIENTIFIC RULE

Không được giả định:

> Dữ liệu lịch sử có thể dự đoán kỳ tiếp theo.

Không được giả định:

> Bao 18 được chọn bởi thuật toán chắc chắn tốt hơn Bao 18 random.

Không được giả định:

> HOT, COLD, momentum, gap hoặc AI tạo predictive edge.

Tất cả đều là hypothesis.

Hệ thống phải có khả năng kết luận:

```text
NO_RANKING_EDGE_FOUND
```

Đây là kết quả hợp lệ.

---

# 3. PRIMARY RESEARCH QUESTION

Câu hỏi trung tâm:

> Có thể dùng duy nhất dữ liệu tồn tại trước một kỳ quay để tạo ranking 01–45, sao cho 6 số của kỳ quay kế tiếp có xu hướng xuất hiện gần đầu ranking hơn random hay không?

Đối với kỳ quay t:

```text
History:
draw_1 ... draw_(t-1)

        ↓

Ranking model

        ↓

Rank 01–45

        ↓

Actual draw t
```

Tuyệt đối không sử dụng draw t để xây feature cho draw t.

---

# 4. FINAL RESEARCH TARGET

Không trực tiếp dự đoán 6 số.

Target là:

```text
45
↓
18
↓
17
↓
16
↓
15
↓
14
↓
...
↓
7
```

Nhưng phải tuân theo:

```text
45→18 chưa pass
→ không được claim 15

15 chưa pass
→ không được claim 14

...

STOP WHEN EDGE DISAPPEARS
```

Không ép thuật toán phải xuống 7.

Có thể kết luận:

```text
Minimum defensible pool = 16
```

hoặc:

```text
No pool has demonstrated edge
```

---

# 5. TECHNOLOGY CONSTRAINTS

Toàn bộ dự án dùng Python.

Recommended runtime:

```text
Python >= 3.12
```

Core stack:

```text
Streamlit
Pandas or Polars
NumPy
SciPy
Statsmodels
scikit-learn
httpx
BeautifulSoup4
lxml
Pydantic
DuckDB
PyArrow
Plotly
Altair optional
pytest
Hypothesis
```

Optional:

```text
LightGBM
XGBoost
OR-Tools
```

chỉ thêm khi justified.

Không thêm dependency chỉ để “trông mạnh”.

---

# 6. STRICTLY FORBIDDEN STACK

Không sử dụng:

```text
Next.js
React
Vue
Angular
TypeScript
Node.js backend
Express
Firebase
Supabase
```

Không dùng custom JavaScript nếu Streamlit native component giải quyết được.

Nếu thực sự cần custom component:

phải giải thích lý do trước.

---

# 7. PROJECT ARCHITECTURE

Thiết kế clean architecture:

```text
vietlott-quant-lab/
│
├── app.py
│
├── pages/
│   ├── 01_overview.py
│   ├── 02_data_library.py
│   ├── 03_number_lab.py
│   ├── 04_candidate_pool.py
│   ├── 05_ab_tournament.py
│   ├── 06_compression_frontier.py
│   ├── 07_prospective.py
│   └── 08_system_health.py
│
├── src/
│   ├── config/
│   ├── data/
│   ├── features/
│   ├── ranking/
│   ├── research/
│   ├── statistics/
│   ├── prospective/
│   ├── optimization/
│   ├── provenance/
│   ├── observability/
│   └── ui/
│
├── data/
│   ├── raw/
│   ├── processed/
│   ├── snapshots/
│   └── manifests/
│
├── artifacts/
│   ├── experiments/
│   ├── prospective/
│   └── reports/
│
├── tests/
├── scripts/
├── docs/
├── pyproject.toml
├── README.md
└── .github/workflows/
```

Không tạo file khổng lồ.

Không nhét research logic vào Streamlit page.

UI chỉ gọi service/research layer.

---

# 8. DATA SOURCE

Nguồn duy nhất:

```text
vietlott.vn
```

Trước khi code parser:

1. kiểm tra cấu trúc site hiện tại;
2. xác định endpoint chính thức;
3. xác định HTML/API/XHR source thực tế;
4. kiểm tra pagination;
5. kiểm tra Mega 6/45 product identifier;
6. ghi lại source discovery.

Không hard-code DOM selector mà không có fallback strategy.

---

# 9. RESPONSIBLE FETCHING

Crawler phải:

- rate-limit;
- retry có backoff;
- timeout;
- User-Agent rõ ràng;
- cache local;
- không request lại history cũ vô ích;
- không flood vietlott.vn;
- incremental sync;
- fail gracefully.

Nếu site thay đổi:

```text
DO NOT silently return empty dataset
```

Phải báo:

```text
SOURCE_SCHEMA_CHANGED
```

---

# 10. RAW DATA IMMUTABILITY

Mỗi response chính thức phải có khả năng snapshot.

Lưu:

```text
source_url
fetched_at
HTTP status
content hash
parser version
```

Raw snapshot không được silently overwrite.

Processed data phải truy ngược được về raw source.

---

# 11. CANONICAL DRAW SCHEMA

Sử dụng Pydantic.

Ví dụ:

```python
class DrawRecord(BaseModel):
    product: Literal["mega645"]
    draw_id: str
    draw_date: date
    numbers: tuple[int, int, int, int, int, int]
    source_url: str
    fetched_at: datetime
```

Validation:

- exactly 6 numbers;
- unique;
- integer;
- 1–45;
- sorted canonical representation;
- draw_id unique;
- date valid.

---

# 12. DATA INTEGRITY

Phải kiểm tra:

```text
duplicate draw_id
duplicate date
duplicate result
missing IDs
invalid numbers
changed historical draw
date ordering
schema drift
```

Nếu draw lịch sử đã tồn tại nhưng Vietlott trả result khác:

```text
FAIL CLOSED
```

Không overwrite tự động.

Lưu:

```text
OLD
NEW
SOURCE
TIMESTAMP
HASH
```

và yêu cầu reconciliation.

---

# 13. STORAGE

Dùng:

```text
DuckDB
+
Parquet
```

Recommended:

```text
raw snapshots → filesystem
canonical data → Parquet
metadata / sync state → DuckDB
```

Không cần PostgreSQL trong research MVP.

DuckDB phải đủ cho:

- historical analysis;
- feature extraction;
- experiment artifacts;
- local production deployment.

---

# 14. DATA MANIFEST

Mỗi canonical dataset phải có manifest:

```text
record_count
first_draw_id
last_draw_id
first_date
last_date
dataset_sha256
parser_version
source
last_sync
validation_status
```

Mọi experiment phải ghi dataset hash.

---

# 15. NUMBER LIBRARY 01–45

Xây một library cho từng số:

```text
01
02
...
45
```

Tại mỗi cutoff t, tính feature chỉ từ:

```text
draws < t
```

---

# 16. MULTI-SCALE WINDOWS

Mandatory windows:

```text
15
30
45
60
90
120
180
270
365
500
750
1000
ALL
```

Không mặc định window nào predictive.

Mỗi window là một research hypothesis.

---

# 17. FREQUENCY FEATURES

Cho mỗi number:

```text
count
frequency
expected_frequency
absolute_deviation
relative_deviation
z_score
percentile
```

tại mọi window.

---

# 18. RECENCY FEATURES

Tính:

```text
current gap
previous gap
mean historical gap
median gap
gap std
gap percentile
gap z-score
current_gap / mean_gap
```

---

# 19. MOMENTUM FEATURES

Ví dụ:

```text
freq15 - freq90
freq30 - freq180
freq60 - freq365
freq90 - freq500
```

Tính:

- slope;
- acceleration;
- short-vs-long divergence.

---

# 20. MEAN-REVERSION FEATURES

Đo:

```text
distance from long-term mean
extreme short-term deviation
historical tendency after similar deviation
```

Không assume mean reversion.

Phải A/B test với momentum.

---

# 21. STABILITY FEATURES

Cho mỗi number:

```text
window-to-window variance
rank stability
frequency volatility
gap volatility
regime consistency
```

---

# 22. CO-OCCURRENCE FEATURES

Nghiên cứu:

```text
pair frequency
expected pair frequency
pair lift
pair residual
conditional probability
rolling pair stability
```

Không dùng raw pair count trực tiếp làm predictive score.

Phải chuẩn hóa theo null expectation.

Triplets chỉ thêm nếu có lý do.

---

# 23. SHRINKAGE

Short window rất noisy.

Implement shrinkage:

```text
local estimate
↓
reliability
↓
long-run prior
↓
shrunk estimate
```

Có thể dùng:

- empirical Bayes;
- beta-binomial approximation;
- weighted shrinkage.

Không để 15-draw extreme tự động thống trị ranking.

---

# 24. NUMBER FEATURE VECTOR

Output cuối cho mỗi number:

```text
number
freq_15
freq_30
...
freq_all

z_15
z_30
...

gap
gap_z
gap_percentile

momentum_short
momentum_medium

mean_reversion_score

stability

pair_signal

shrinkage_signal
```

Phải deterministic.

---

# 25. FULL 01–45 RANKING

Mọi model phải output:

```text
Rank 1
Rank 2
...
Rank 45
```

Không chỉ output 18 số.

Data model:

```python
@dataclass(frozen=True)
class RankedNumber:
    number: int
    score: float
    rank: int
```

---

# 26. INITIAL MODEL FAMILY

Mandatory:

```text
MODEL A
ALL-HISTORY baseline

MODEL B
single-window frequency

MODEL C
multi-scale frequency

MODEL D
momentum

MODEL E
mean reversion

MODEL F
multi-scale + momentum + reversion

MODEL G
Bayesian / shrinkage

MODEL H
pair-aware

MODEL I
adaptive-window
```

Không thêm ML ngay.

---

# 27. MACHINE LEARNING POLICY

ML chỉ được triển khai khi classical models đã có baseline.

Candidates:

```text
logistic regression
regularized linear model
gradient boosting
LightGBM / XGBoost
learning-to-rank
```

Không dùng neural network mặc định.

Không dùng deep learning chỉ để marketing.

ML phải thắng simpler champion trên Validation và Test.

Nếu không:

```text
PRUNE ML
```

---

# 28. RANDOM BASELINE

Đối với pool m:

\[
K = |Pool_m \cap ActualDraw|
\]

Exact null:

\[
P(K=k)=
\frac{\binom{m}{k}\binom{45-m}{6-k}}
{\binom{45}{6}}
\]

Implement bằng SciPy hoặc exact combinatorics.

Không dùng Monte Carlo khi exact formula tồn tại.

---

# 29. CORE METRICS

Đối với mỗi model và pool:

```text
Mean K
P(K >= 3)
P(K >= 4)
P(K >= 5)
P(K = 6)
```

Ngoài ra:

```text
mean winner rank
median winner rank
best winner rank
worst winner rank
```

---

# 30. MAX WINNER RANK

Cho winning numbers:

```text
r1 ... r6
```

định nghĩa:

\[
MaxWinnerRank=\max(r_1,...,r_6)
\]

Đây là metric cực quan trọng.

---

# 31. MINIMUM CONTAINMENT POOL

Định nghĩa:

\[
MCP_t = MaxWinnerRank_t
\]

Interpretation:

```text
MCP = 14
```

nghĩa là:

> Top 14 đã chứa đủ cả 6 winning numbers.

Phải đo:

```text
P(MCP <= 18)
P(MCP <= 17)
...
P(MCP <= 7)
```

---

# 32. RESEARCH SPLIT

Không random split.

Chronological only:

```text
Development = 50%
Validation  = 25%
Test        = 25%
```

Không shuffle.

---

# 33. DEVELOPMENT

Được phép:

- tạo features;
- thử windows;
- tune weights;
- tạo models;
- exploratory analysis.

---

# 34. VALIDATION

Chỉ dùng để:

- chọn window;
- chọn feature set;
- chọn model;
- chọn hyperparameters;
- chọn minimum pool candidate.

Sau khi chọn champion:

```text
FREEZE
```

---

# 35. TEST

Test chỉ được mở sau khi freeze.

Không tune sau khi thấy Test.

Nếu fail:

```text
HOLDOUT_SIGNAL_NOT_CONFIRMED
```

Không quay lại Test rồi chỉnh model.

Model mới phải có protocol mới.

---

# 36. PROSPECTIVE

Sau Test:

freeze prediction/ranking trước draw tương lai.

Lưu:

```text
target_draw
ranking_01_45
top18
...
top7
model_id
model_hash
feature_hash
dataset_hash
frozen_at
```

Sau khi kết quả Vietlott xuất hiện:

append score.

Không sửa frozen record.

---

# 37. HASH CHAIN

Prospective records phải append-only.

Mỗi record chứa:

```text
record_hash
previous_hash
```

Nếu history bị sửa:

verification fail.

---

# 38. WINDOW TOURNAMENT

Round đầu:

```text
15
30
45
60
90
120
180
270
365
500
750
1000
ALL
```

So sánh trên Development.

Top candidates sang Validation.

Không để Test chọn window.

---

# 39. MODEL A/B TOURNAMENT

Sequence:

```text
Round 1
ALL-history
vs
best rolling window

Round 2
winner
vs
multi-scale

Round 3
winner
vs
momentum

Round 4
winner
vs
mean reversion

Round 5
winner
vs
shrinkage

Round 6
winner
vs
pair-aware

Round 7
winner
vs
adaptive-window

Round 8
optional ML challenger
```

Nếu hòa:

model đơn giản thắng.

---

# 40. PRIMARY ENDPOINT

Primary research endpoint:

\[
Mean(K)
\]

Pool 18 random expectation:

\[
E[K]=6\times18/45=2.4
\]

Model phải vượt null không chỉ numerically mà phải có:

- statistical credibility;
- stability;
- practical significance.

---

# 41. SECONDARY ENDPOINTS

Mandatory:

```text
P(K≥4)
P(K≥5)
P(K=6)
MCP
winner rank distribution
```

Không optimize trực tiếp chỉ P6.

---

# 42. WHY NOT P6 PRIMARY

Jackpot containment rất rare.

Nếu optimize Hit6:

```text
high variance
+
low power
+
overfitting risk
```

Vì vậy P6 là:

```text
ultimate outcome
```

nhưng không phải sole model-selection endpoint.

---

# 43. MULTIPLE TESTING

Bắt buộc xử lý:

- nhiều models;
- nhiều windows;
- nhiều pool sizes;
- nhiều features.

Sử dụng:

```text
Holm-Bonferroni
```

hoặc phương pháp có justification.

Không report raw p-value rồi bỏ qua multiplicity.

---

# 44. DEPENDENCE

Rolling windows tạo temporal dependence.

Sử dụng khi phù hợp:

```text
Newey-West HAC
block bootstrap
paired permutation
```

Không giả định observations độc lập một cách mù quáng.

---

# 45. NEGATIVE CONTROLS

Mandatory:

```text
uniform random ranking
seeded random ranking
shuffled-history model
synthetic fair lottery
```

Các model này không được tạo edge ổn định.

---

# 46. POSITIVE LEAKAGE CONTROL

Tạo deliberate reverse-peek model:

```text
actual draw
↓
force winners to top ranks
```

Expected:

```text
100% containment
```

Nếu control này không thắng mạnh:

test harness có bug.

Nhãn bắt buộc:

```text
INVALID_AS_PREDICTIVE_EVIDENCE
```

---

# 47. LEAK TEST

Mọi feature function phải reject:

```text
draw_date >= target_date
```

Unit test bắt buộc.

Không rely vào comment.

---

# 48. FEATURE ABLATION

Champion model phải trải qua:

```text
remove frequency
remove gap
remove momentum
remove reversion
remove stability
remove pair
remove shrinkage
```

Measure delta.

Classify:

```text
USEFUL
NEUTRAL
HARMFUL
```

HARMFUL feature phải loại.

---

# 49. RED-TEAM

Stress test:

- start date;
- end date;
- window perturbation;
- seed perturbation;
- remove recent draws;
- early / middle / late;
- regime split;
- shuffled order;
- alternative normalization;
- small model parameter changes.

Nếu tiny change làm edge biến mất:

```text
FRAGILE_SIGNAL
```

---

# 50. POOL 18 GATE

45→18 chỉ pass nếu:

```text
Mean K > null
AND
Validation positive
AND
Test positive
AND
effect practically meaningful
AND
robustness acceptable
AND
no leakage
```

Nếu fail:

```text
NO_VERIFIED_18_POOL_EDGE
```

---

# 51. COMPRESSION LADDER

Sau 18:

```text
18
17
16
15
14
13
12
11
10
9
8
7
```

Tất cả lấy từ cùng frozen ranking trước tiên.

Không train model riêng cho từng m ngay lập tức.

---

# 52. NESTED POOLS

Mandatory default:

\[
S_7 \subset S_8 \subset ... \subset S_{18}
\]

Top-m của ranking.

Sau này mới test specialized models.

---

# 53. COMPRESSION FRONTIER

Output:

```text
Pool
Random Mean K
Model Mean K
Delta
P4
P5
P6
MCP rate
Full Bao tickets
Full Bao cost
Evidence status
```

---

# 54. BAO COMBINATORICS

Full Bao m:

\[
Tickets(m)=\binom{m}{6}
\]

Cost:

\[
Cost(m)=10,000\times\binom{m}{6}
\]

Jackpot containment null:

\[
P_6(m)=
\frac{\binom{m}{6}}{\binom{45}{6}}
\]

Must calculate exactly.

---

# 55. COST EFFICIENCY

Không được claim:

> Bao15 hiệu quả hơn Bao18

chỉ vì rẻ hơn.

Phải tính:

```text
model lift
per cost
vs
random same pool
```

Chỉ gọi cost-efficiency gain nếu algorithm tạo incremental evidence.

---

# 56. STAGE 2 TICKET OPTIMIZATION

Chỉ làm sau Candidate Pool Research.

Ví dụ:

```text
Top15 candidate pool
↓
C(15,6)
↓
budget
↓
choose subset of tickets
```

Optimization candidates:

```text
covering design
set packing
greedy marginal coverage
CP-SAT
integer programming
```

Tách rõ:

```text
PREDICTIVE RANKING
≠
COMBINATORIAL COVERAGE
```

---

# 57. STREAMLIT UI

UI phải rõ ràng, desktop-first nhưng responsive.

Sidebar:

```text
Overview
Data Library
Number Lab
Candidate Pool
A/B Tournament
Compression Frontier
Prospective
System Health
```

---

# 58. OVERVIEW PAGE

Hiển thị:

```text
Scientific Verdict

Dataset:
draw count
first draw
latest draw
last sync
source
hash

Research:
best model
best window
current evidence level

Candidate Pool:
best validated cutoff
```

---

# 59. DATA LIBRARY PAGE

Hiển thị:

- toàn bộ draws;
- filter date;
- draw ID;
- official source link;
- integrity status;
- sync;
- freshness;
- validation.

Không gọi network mỗi Streamlit rerun.

Dùng cache hợp lý.

---

# 60. NUMBER LAB PAGE

Cho phép chọn:

```text
01 ... 45
```

Hiển thị:

- lifetime history;
- rolling frequencies;
- gap history;
- momentum;
- mean reversion;
- rank over time;
- pair relationships.

Đây chính là:

## thư viện từng con số.

---

# 61. NUMBER RANKING PAGE

Hiển thị bảng:

```text
Rank
Number
Score
Short
Medium
Long
Gap
Momentum
Reversion
Stability
```

Không gọi score là probability trừ khi calibration evidence thật sự đủ.

---

# 62. CANDIDATE POOL PAGE

Selector:

```text
18 → 7
```

Hiển thị:

```text
Top m numbers
Mean K
Random Mean K
P4
P5
P6
MCP
Lift
Evidence
```

---

# 63. A/B TOURNAMENT PAGE

Hiển thị:

```text
Model A
vs
Model B
```

Metrics:

- Development;
- Validation;
- Test;
- effect;
- adjusted p;
- robustness.

Winner phải do research engine quyết định.

Không hard-code UI winner.

---

# 64. COMPRESSION FRONTIER PAGE

Chart:

```text
Pool size
vs
Containment performance
```

Chart:

```text
Pool size
vs
Full Bao cost
```

Chart:

```text
Cost
vs
Evidence-adjusted containment
```

Highlight Pareto frontier.

---

# 65. PROSPECTIVE PAGE

Hiển thị:

```text
Frozen rankings
pending
scored
hash chain
target draw
frozen_at
model
```

Không cho sửa record.

---

# 66. SCIENTIFIC STATUS

Dùng các trạng thái:

```text
NO_RANKING_EDGE_FOUND
EXPLORATORY_SIGNAL
VALIDATION_SIGNAL
HOLDOUT_SIGNAL
PROSPECTIVE_SIGNAL
```

Không dùng:

```text
AI PREDICTED
LIKELY WINNER
GUARANTEED NUMBERS
```

---

# 67. STREAMLIT CACHING

Dùng:

```python
@st.cache_data
@st.cache_resource
```

đúng mục đích.

Không cache:

- mutable prospective decisions;
- stale network status vô thời hạn.

Cache key phải phụ thuộc:

```text
dataset hash
model version
protocol hash
```

---

# 68. PERFORMANCE

Target:

- app first meaningful load hợp lý;
- historical feature computation cached;
- không recompute toàn bộ 1,500+ draws mỗi click;
- vectorize khi phù hợp;
- DuckDB pushdown;
- Parquet column pruning.

Profile trước khi optimize.

---

# 69. BACKGROUND PROCESS POLICY

Streamlit UI không được phụ thuộc một job vô hình.

Long-running research command nên chạy qua CLI:

```text
python -m scripts.run_window_tournament
python -m scripts.run_model_tournament
```

UI đọc artifact đã hoàn thành.

---

# 70. EXPERIMENT ARTIFACT

Mọi experiment phải lưu JSON:

```text
experiment_id
protocol_hash
dataset_hash
model
features
windows
hyperparameters
development_results
validation_results
test_results
generated_at
git_commit
```

Không chỉ lưu Markdown.

---

# 71. PROVENANCE

Experiment ID không được chỉ dựa trên timestamp.

Identity phải bao gồm:

```text
dataset hash
protocol hash
model config hash
```

---

# 72. REPRODUCIBILITY

Mọi RNG phải seeded.

Không dùng global uncontrolled randomness.

Artifact phải reproduce được từ:

```text
git commit
dataset hash
protocol
seed
```

---

# 73. PYTHON QUALITY

Mandatory:

```text
type hints
dataclasses / Pydantic
ruff
mypy
pytest
```

Không để core research là loosely typed dictionaries khắp nơi.

---

# 74. TESTING PYRAMID

Unit:

- combinatorics;
- ranking;
- feature calculations;
- leakage;
- hashes.

Property:

- pool sizes;
- uniqueness;
- ranking permutations;
- probability sums.

Integration:

- vietlott parser;
- sync;
- DuckDB;
- artifacts.

Research:

- random controls;
- reverse-peek;
- walk-forward.

UI:

- Streamlit smoke;
- page render;
- artifact failure fallback.

---

# 75. PROPERTY TESTS

Sử dụng Hypothesis.

Ví dụ invariants:

```text
ranking = permutation 1..45

Top15 ⊂ Top18

0 <= probability <= 1

sum hypergeometric PMF = 1

MCP between 6 and 45

no duplicate numbers
```

---

# 76. CI PIPELINE

GitHub Actions:

```text
Install
↓
Ruff
↓
Mypy
↓
Unit tests
↓
Property tests
↓
Integration tests
↓
Data parser fixture tests
↓
Leakage tests
↓
Research control tests
↓
Streamlit startup smoke
```

Không fetch toàn bộ Vietlott production history mỗi CI run.

Dùng fixtures.

---

# 77. LIVE DATA CHECK

Tách khỏi deterministic CI.

Scheduled/manual workflow:

```text
live source availability
schema compatibility
latest draw check
```

Failure không được corrupt canonical dataset.

---

# 78. LOGGING

Structured Python logging:

```text
timestamp
level
event
source
draw_id
duration
status
```

Không print lung tung.

---

# 79. HEALTH STATUS

Streamlit System Health page:

```text
Source reachable
Parser status
Dataset integrity
Dataset freshness
DuckDB
Experiment artifacts
Prospective chain
App version
```

---

# 80. SECURITY

Review:

- SSRF;
- unsafe URLs;
- malformed HTML;
- oversized responses;
- decompression bombs;
- arbitrary pickle loading;
- path traversal;
- unsafe YAML;
- dependency vulnerabilities.

Không dùng pickle cho untrusted artifact.

Prefer:

```text
JSON
Parquet
DuckDB
```

---

# 81. CONFIGURATION

Dùng:

```text
.env
+
Pydantic Settings
```

Không hard-code secrets.

Nhưng dữ liệu Vietlott public không cần secret.

---

# 82. DEPLOYMENT

Target options:

```text
Streamlit Community Cloud
Docker
Cloud Run
Railway
Render
VM
```

Tạo Dockerfile production.

Không khóa architecture vào một provider.

---

# 83. DOCKER

Use:

```text
python:3.12-slim
```

non-root user.

Healthcheck.

Dependency pinning.

---

# 84. DOCUMENTATION

Mandatory:

```text
README.md
docs/architecture.md
docs/data-source.md
docs/research-protocol.md
docs/statistical-null.md
docs/prospective.md
docs/deployment.md
docs/runbook.md
```

---

# 85. README MUST STATE

Rõ ràng:

> This application does not claim to predict Vietlott outcomes.

Và:

> Historical patterns are research hypotheses, not guaranteed predictive signals.

---

# 86. IMPLEMENTATION PHASES

## Phase 0

Repository + tooling + architecture.

## Phase 1

Official Vietlott ingestion.

## Phase 2

Canonical dataset + DuckDB.

## Phase 3

Number Library 01–45.

## Phase 4

Exact null mathematics.

## Phase 5

Ranking engine.

## Phase 6

Window tournament.

## Phase 7

Model tournament.

## Phase 8

45→18 validation.

## Phase 9

Compression 18→7.

## Phase 10

Prospective freeze/scoring.

## Phase 11

Streamlit production UI.

## Phase 12

Hardening / CI / Docker.

---

# 87. IMPORTANT EXECUTION RULE

Không xây toàn bộ 20 models cùng lúc.

Iterative:

```text
baseline
↓
test
↓
evidence
↓
next model
```

Mỗi complexity layer phải justify chính nó.

---

# 88. ROUND 1 REQUIRED MODELS

Implement trước:

```text
A = HOT18 current-style baseline
B = Multi-Scale Shrinkage Ranking
C = Random ranking
```

Không ML.

---

# 89. MULTI-SCALE SHRINKAGE INITIAL VERSION

Recommended windows:

```text
30
60
90
180
365
ALL
```

Features:

```text
standardized frequency
gap
short-vs-medium momentum
medium-vs-long divergence
long-term prior
stability
```

Generate score for all 45 numbers.

---

# 90. ROUND 1 SUCCESS

Multi-Scale Shrinkage không cần “thắng Jackpot”.

Phải kiểm tra:

```text
Mean K
P4+
P5+
P6
MCP
rank quality
```

against exact random.

---

# 91. STOPPING RULE

Nếu Multi-Scale không vượt random/HOT robustly:

không tự động thêm ML.

Thử:

```text
mean reversion
adaptive window
```

Nếu vẫn fail:

```text
NO_RANKING_EDGE_FOUND
```

---

# 92. PRODUCTION DEFINITION OF DONE

Project chỉ được gọi production-grade khi:

- official data ingestion robust;
- no silent empty sync;
- canonical validation;
- reproducible dataset hash;
- anti-leak tests;
- exact null;
- full ranking;
- A/B tournament;
- holdout protocol;
- prospective machinery;
- compression frontier;
- Streamlit UI stable;
- tests green;
- CI green;
- Docker works;
- documentation complete;
- no misleading prediction claims.

---

# 93. FINAL REPORT

Sau khi hoàn thành, phải xuất:

```text
HEAD commit
Python version
Data latest draw
Dataset hash
Total draws

Best model
Best windows
Best pool
Minimum defensible pool

Mean K
Random Mean K
P4 lift
P5 lift
P6 lift
MCP distribution

Development
Validation
Test
Prospective

Scientific verdict
Production verdict
```

---

# 94. FINAL SCIENTIFIC VERDICT

Chỉ được chọn một:

```text
NO_RANKING_EDGE_FOUND
```

hoặc:

```text
EXPLORATORY_SIGNAL_ONLY
```

hoặc:

```text
VALIDATION_SIGNAL_FOUND
```

hoặc:

```text
HOLDOUT_SIGNAL_FOUND
```

hoặc:

```text
PROSPECTIVE_SIGNAL_FOUND
```

---

# 95. FINAL PRODUCT VERDICT

Riêng engineering:

```text
NOT_PRODUCTION_READY
```

hoặc:

```text
PRODUCTION_READY
```

Scientific edge và production readiness là hai khái niệm độc lập.

Một app có thể:

```text
PRODUCTION_READY
+
NO_RANKING_EDGE_FOUND
```

Đó vẫn là kết quả hoàn toàn hợp lệ.

---

# 96. ABSOLUTE PRINCIPLE

Không tối ưu để chứng minh hypothesis đúng.

Tối ưu để:

> làm hypothesis dễ bị bác bỏ nhất có thể.

Nếu nó vẫn sống sót qua:

```text
walk-forward
validation
holdout
red-team
prospective
```

thì lúc đó mới coi signal đáng nghiên cứu tiếp.

---

# 97. CORE PRODUCT LOOP

```text
vietlott.vn
        ↓
Official Data Library
        ↓
01–45 Number Library
        ↓
Multi-Scale Features
        ↓
Ranking 01–45
        ↓
Top18
        ↓
Exact Random Comparison
        ↓
A/B Tournament
        ↓
Validation
        ↓
Holdout
        ↓
Compression 18→7
        ↓
Prospective
        ↓
Cost / Evidence Frontier
```

---

# 98. FINAL DIRECTIVE

Build this as a real quantitative research product, not a lottery-number generator.

The application must make these distinctions impossible to miss:

```text
DESCRIPTIVE PATTERN
≠
PREDICTIVE SIGNAL

PREDICTIVE SIGNAL
≠
PROVEN EDGE

CANDIDATE POOL
≠
GUARANTEED WINNERS

COST REDUCTION
≠
EFFICIENCY GAIN

BACKTEST
≠
PROSPECTIVE EVIDENCE

RANKING
≠
PROBABILITY
```

The highest-value output is not:

> “Here are the numbers to play.”

It is:

> “Given all evidence available before the draw, this model ranks 01–45 in this order; Top-m performs this much above or below the exact random baseline, with this evidence level, cost and uncertainty.”

Only evidence decides whether the research continues from:

```text
45 → 18 → 15 → ... → 7
```

or stops.