# Phase 2: 자료구조 제대로 사용하기

> **목표**: "리스트에 for 돌려서 append" 습관에서 →
> "상황에 맞는 자료구조를 골라서, 한 줄로 데이터를 변환하는" 수준으로
> **ROI**: ⭐⭐ A등급 — 이미 쓰고 있지만, 숙달도가 코드 품질을 좌우하는 영역
> **Python 버전**: 3.9+ (dict `|` 병합), 3.10+ (match-case), 3.12+ (type 문)

---

## 1. 핵심 개념 정리

### 1-1. Python 자료구조 선택 맵

어떤 자료구조를 사용해야 할지 모를 때, 이 의사결정 트리를 따지면 됨.

```
데이터를 담아야 한다
│
├─ 순서가 중요한가?
│   ├─ Yes → 변경 가능? → Yes → list
│   │                   → No  → tuple
│   └─ No  → 중복 허용? → Yes → dict (키-값)
│                       → No  → set
│
├─ 키로 값을 찾아야 하는가?
│   └─ Yes → dict
│       ├─ 기본값이 필요? → defaultdict
│       ├─ 개수를 세야? → Counter
│       └─ 필드명이 고정? → NamedTuple / TypedDict / dataclass
│
└─ 큐/스택이 필요한가?
    ├─ 양쪽 끝에서 삽입/삭제 → deque
    └─ 우선순위 기반 → heapq
```

### 1-2. 용어 풀이

| 용어 | 쉬운 설명 |
|------|-----------|
| **컴프리헨션 (comprehension)** | 반복문을 한 줄로 압축해서 list/dict/set을 만드는 문법. `[x for x in items]` |
| **언패킹 (unpacking)** | 묶여 있는 데이터를 풀어서 개별 변수에 나눠 담는 것. `a, b = [1, 2]` |
| **스프레드 연산자 (`*`, `**`)** | 리스트는 `*`로, 딕셔너리는 `**`로 "풀어헤치는" 연산자 |
| **해시 가능 (hashable)** | dict의 키나 set의 원소가 될 수 있는 값. 불변(immutable) 타입만 가능. str, int, tuple은 O, list는 X |
| **뮤터블 (mutable)** | 생성 후 내용을 바꿀 수 있는 객체. list, dict, set |
| **이뮤터블 (immutable)** | 생성 후 내용을 바꿀 수 없는 객체. str, int, float, tuple, frozenset |
| **지연 평가 (lazy evaluation)** | 값을 미리 만들지 않고, 실제로 필요할 때 하나씩 만드는 방식. 제너레이터가 대표적 (Phase 5에서 상세) |

---

## 2. Good vs. Bad 예시

### 2-1. 리스트 컴프리헨션 - for + append 탈출

```python
# ❌ Bad: 빈 리스트 → for 루프 → append 패턴
orders = [
    {"product": "노트북", "amount": 1_200_000, "status": "completed"},
    {"product": "마우스", "amount": 35_000, "status": "cancelled"},
    {"product": "키보드", "amount": 89_000, "status": "completed"},
    {"product": "모니터", "amount": 450_000, "status": "completed"},
]

completed_amounts = []
for order in orders:
    if order["status"] == "completed":
        completed_amounts.append(order["amount"])
# → [1200000, 89000, 450000]
```

```python
# ✅ Good: 리스트 컴프리헨션
orders = [
    {"product": "노트북", "amount": 1_200_000, "status": "completed"},
    {"product": "마우스", "amount": 35_000, "status": "cancelled"},
    {"product": "키보드", "amount": 89_000, "status": "completed"},
    {"product": "모니터", "amount": 450_000, "status": "completed"},
]

completed_amounts = [
    order["amount"]
    for order in orders
    if order["status"] == "completed"
]
# → [1200000, 89000, 450000]
```

> 💡 **컴프리헨션 읽는 법** (위에서 아래로):
> ```
> [                              ← 결과를 리스트로 모아라
>     order["amount"]            ← 각 원소에서 이 값을 꺼내서
>     for order in orders        ← orders를 하나씩 순회하면서
>     if order["status"] == "completed"  ← 이 조건을 만족하는 것만
> ]
> ```

**컴프리헨션 vs for 루프, 언제 뭘 쓰나?**

| 상황 | 추천 | 이유 |
|------|------|------|
| 단순 변환 + 필터 | 컴프리헨션 | 한 줄로 의도가 명확 |
| 중첩 2단계까지 | 컴프리헨션 가능 | 단, 가독성 확인 필요 |
| 중첩 3단계 이상 | for 루프 | 컴프리헨션이 오히려 가독성 해침 |
| 부수 효과(side effect)가 있을 때 | for 루프 | API 호출, 파일 쓰기 등 |
| 결과를 안 쓰고 동작만 실행할 때 | for 루프 | `[print(x) for x in items]`는 안티패턴 |

---

### 2-2. 딕셔너리 컴프리헨션

```python
# ❌ Bad: dict를 for 루프로 수동 구성
products = [
    {"id": "P001", "name": "노트북", "price": 1_200_000},
    {"id": "P002", "name": "마우스", "price": 35_000},
    {"id": "P003", "name": "키보드", "price": 89_000},
]

price_map = []
for p in products:
    prcie_map[p["id"]] = p["price"]
# → {"P001": 1200000, "P002": 35000, "P003": 89000}
```

```python
# ✅ Good: 딕셔너리 컴프리헨션
price_map = {p["id"]: p["price"] for p in products}
# → {"P001": 1200000, "P002": 35000, "P003": 89000}

# 조건 필터링 + 변환 동시에
premium_products = {
    p["id"]: f"₩{p['price']:,}"
    for p in products
    if p["price"] >= 50_000
}
# → {"P001": "₩1,200,000", "P003": "₩89,000"}
```

---

### 2-3. 셋 컴프리헨션 & 셋 연산 - 집합 로직

```python
# ❌ Bad: 중복 제거를 리스트 + in으로 수동 처리
visited_pages = ["/home", "/product", "/cart", "/home", "/product", "/checkout"]

unique_pages = []
for page in visited_pages:
    if page not in unique_pages:    # ← 리스트의 in은 O(n). 느림
        unique_pages.append(page)
```

```python
# ✅ Good: set으로 중복 제거
unique_pages = set(visited_pages)
# → {"/home", "/product", "/cart", "/checkout"}

# 셋 컴프리헨션 (조건부 중복 제거)
product_pages = {page for page in visited_pages if page.startswith("/product")}
# → {"/product"}
```

**셋 연산으로 비즈니스 로직 표현하기:**

```python
# 시나리오: 유저 세그먼트 분석
jan_buyers = {"김윤섭", "이민수", "박지영", "최한슬"}
feb_buyers = {"이민수", "최한솔", "정수현", "강태오"}

# 교집합: 1월 AND 2월 모두 구매한 유저 (리텐션)
retained = jan_buyers & feb_buyers
# → {"이민수", "최한솔"}

# 차집합: 1월에 샀지만 2월에 안 산 유저 (이탈)
churned = jan_buyers - feb_buyers
# → {"김윤섭", "박지영"}

# 차집합: 2월 신규 유저
new_users = feb_buyers - jan_buyers
# → {"정수현", "강태오"}

# 합집합 : 1월 OR 2월 한 번이라도 구매한 유저
all_buyers = jan_buyers | feb_buyers
# → {"김윤섭", "이민수", "박지영", "최한솔", "정수현", "강태오"}

# 대칭차집합: 한 달만 구매한 유저 (비정기 구매자)
one_time = jan_buyers ^ feb_buyers
# → {"김윤섭", "박지영", "정수현", "강태오"}

# 부분집합: retained가 jan_buyers의 부분집합인지
retained <= jan_buyers
# → True
```

> 💡 **리스트의 `in` vs 셋의 `in`**:
> - `"김윤섭" in 리스트`: 처음부터 끝까지 순차 탐색 → O(n)
> - `"김윤섭" in 셋`: 해시 테이블 조회 → O(1)
> - 원소가 1만 개면 셋이 약 1만 배 빠름

---

### 2-4. 언패킹 - `*`와 `**` 제대로 쓰기

#### (a) 기본 언패킹

```python
# ❌ Bad: 인덱스로 접근
user_data = ("김윤섭", 30, "서울", "VIP")
name = user_data[0]
age = user_data[1]
city = user_data[2]
tier = user_data[3]
```

```python
# ✅ Good: 튜플 언패킹
name, age, city, tier = ("김윤섭", 30, "서울", "VIP")

# 일부만 필요할 때: _ 로 무시
name, _, city, _ = ("김윤섭", 30, "서울", "VIP")

# 첫 번째 + 나머지 분리: * 사용
first, *rest = [1, 2, 3, 4, 5]
# first = 1, rest = [2, 3, 4, 5]

# 첫 번째 + 마지막만: 중간은 *_로 무시
first, *_ , last = [1, 2, 3, 4, 5]
# first = 1, last = 5

# 실전: CSV 파싱에서 헤더와 데이터 분리
lines = ["date,revenue,users", "2024-01,1000000,500", "2024-02,1200000,600"]
header, *data_rows = lines
# header = "data,revenue,users"
# data_rows = ["2024-01,1000000,500", "2024-02,1200000,600"]
```

#### (b) `*` 연산자 - 리스트/튜플 펼치기

```python
# ❌ Bad: 리스트 합치기를 + 연산으로
default_metrics = ["DAU", "MAU", "Revenue"]
custom_metrics = ["LTV", "CAC"]
all_metrics = default_metrics + custom_metrics + ["Churn Rate"]
```

```python
# ✅ Good: * 언패킹으로 합치기
all_metrics = [*default_metrics, *custom_metrics, "Churn Rate"]
# → ["DAU", "MAU", "Revenue", "LTV", "CAC", "Churn Rate"]

# 왜 Good인가?
# 1. + 연산은 왼쪽부터 순서대로 새 리스트를 만듦 (중간 객체 생성)
# 2. * 언패킹은 한 번에 모든 원소를 풀어서 새 리스트 생성
# 3. 리스트 + 튜플 + 제너레이터를 섞어서 합칠 수 있음 (+ 는 같은 타입만 가능)

mixed = [*[1, 2], *(3, 4), *range(5, 8)]
# → [1, 2, 3, 4, 5, 6, 7]
```

#### (c) `**` 연산자 — 딕셔너리 펼치기 & 병합

```python
# ❌ Bad: dict.update()로 병합 (원본 변경됨)
default_config = {"timeout": 30, "retries": 3, "verbose": False}
user_config = {"timeout": 60, "debug": True}

merged = default_config.copy()    # 원본 보호하려면 복사 필요
merged.update(user_config)
```

```python
# ✅ Good: ** 언패킹으로 병합 (원본 불변)
merged = {**default_config, **user_config}
# → {"timeout": 60, "retries": 3, "verbose": False, "debug": True}
# 뒤에 오는 dict의 값이 우선 (timeout: 30 → 60으로 덮어씀)

# ✅✅ Best (Python 3.9+): | 연산자
merged = default_config | user_config
# → 동일한 결과. 가장 간결

# |= (제자리 병합, update와 동일하지만 더 깔끔)
config = {"timeout": 30}
config |= {"timeout": 60, "debug": True}
# config → {"timeout": 60, "debug": True}
```

> 💡 **dict `|` 연산자 (3.9+)**: set의 합집합 `|`과 같은 문법을 dict에도 적용.
> `{**a, **b}` 보다 읽기 쉽고, 의도("두 dict를 합친다")가 명확.

#### (d) 함수 호출 시 언패킹

```python
# 실전: API 호출 매개변수를 dict로 관리
base_params = {"model": "claude-sonnet-4-6", "max_tokens": 1000}
custom_params = {"temperature": 0.7, "top_p": 0.9}

# ❌ Bad: 하나하나 적기
response = call_api(
    model="claude-sonnet-4-6",
    max_tokens=1000,
    temperature=0.7,
    top_p=0.9,
)

# ✅ Good: ** 언패킹
response = call_api(**base_params, **custom_params)
# → call_api(model="claude-sonnet-4-6", max_tokens=1000, temperature=0.7, top_p=0.9)

# 리스트를 위치 인자로 풀기
date_parts = [2026, 6, 29]
from datetime import date
d = date(*date_parts)  # → date(2026, 6, 29)
```

---

### 2-5. `collections` 모듈 - 특수 목적 자료구조

#### (a) `Counter` - 빈도 세기의 정석

```python
# ❌ Bad: 수동으로 빈도 세기
events = ["page_view", "add_to_cart", "page_view", "purchase",
          "page_view", "add_to_cart", "page_view"]

counts = {}
for event in events:
    if event in counts:
        counts[event] += 1
    else:
        counts[event] = 1
```

```python
# ✅ Good: Counter
from collection import Counter

counts = Counter(events)
# → Counter({"page_view": 4, "add_to_cart": 2, "purchase": 1})

# 가장 많은 N개
counts.most_common(2)
# → [("page_view", 4), ("add_to_cart", 2)]

# Counter끼리 연산 가능
jan_events = Counter({"page_view": 100, "purchase": 20})
feb_events = Counter({"page_view": 150, "purchase": 15})

# 합산
total = jan_events + feb_events
# → Counter({"page_view": 250, "purchase": 35})

# 차이 (음수는 자동 제거)
diff = feb_events - jan_events
# → Counter({"page_view": 50})  ← purchase는 음수(-5)라 제거됨
```

#### (b) `defaultdict` — 키 없음 에러 방지

```python
# ❌ Bad: KeyError 방지를 위한 분기 처리
user_orders: dict[str, list[str]] = {}

orders_data = [
    ("김윤섭", "ORD-001"),
    ("이민수", "ORD-002"),
    ("김윤섭", "ORD-003"),
    ("박지영", "ORD-004"),
]

for user, order_id in orders_data:
    if user not in user_orders:        # 매번 존재 여부 확인
        user_orders[user] = []
    user_orders[user].append(order_id)
```

```python
# ✅ Good: defaultdict
from collections import defaultdict

user_orders: defaultdict[str, list[str]] = defaultdict(list)
# → 없는 키에 접근하면 자동으로 빈 list([])가 생성됨

for user, order_id in order_data:
    user_orders[user].append(order_id)  # if 체크 불필요
# → {"김윤섭": ["ORD-001", "ORD-003"], "이민수": ["ORD-002"], "박지영": ["ORD-004"]}

# 다른 기본값 예시
word_count: defaultdict[str, int] = defaultdict(int)      # 기본값 0
tag_sets: defaultdict[str, set] = defaultdict(set)         # 기본값 빈 set
```

> 💡 **`defaultdict(list)` vs `dict.setdefault()`**:
> ```python
> # setdefault도 비슷한 역할을 하지만, 매번 기본값을 적어야 함
> user_orders.setdefault(user, []).append(order_id)
> # defaultdict는 선언 시점에 한 번만 적으면 됨 → 더 깔끔
> ```

### (c) `deque` - 양방향 큐

```python
# ❌ Bad: list를 큐로 사용
recent_searches: list[str] = []

def add_search(query: str, max_size: int = 5) -> None:
    recent_searches.append(query)
    if len(recent_searches) > max_size:
        recent_searches.pop(0)    # ← 리스트 맨 앞 삭제는 O(n)! 느림
```

```python
# ✅ Good: deque (double-ended queue, 양방향 큐)
from collections import deque

recent_searches: deque[str] = deque(maxlen=5)
# maxlen 설정 시 자동으로 오래된 것 제거

recent_searches.append("노트북")
recent_searches.append("마우스")
recent_searches.append("키보드")
recent_searches.append("모니터")
recent_searches.append("태블릿")
recent_searches.append("이어폰")  # "노트북"이 자동 제거됨
# → deque(["마우스", "키보드", "모니터", "태블릿", "이어폰"], maxlen=5)
```

> 💡 **list.pop(0)은 O(n), deque.popleft()은 O(1)**:
> 리스트는 맨 앞을 제거하면 나머지 모든 원소가 한 칸씩 앞으로 이동해야 해서 느림.
> deque는 양쪽 끝 연산이 모두 O(1). 큐/슬라이딩 윈도우에는 deque가 정답.

---

## 2-6. `NamedTuple` vs `TypedDict` — 구조화된 데이터

```python
# ❌ Bad: 일반 dict로 구조화된 데이터 표현
user = {"name": "김윤섭", "age": 30, "tier": "VIP"}
print(user["nane"])  # ← 오타! KeyError. IDE가 잡아주지 못함
```

```python
# ✅ Good 옵션 1: NamedTuple — 불변(immutable) 구조체
from typing import NamedTuple

class UserProfile(NamedTuple):
    name: str
    age: int
    tier: str

user = UserProfile(name="김윤섭", age=30, tier="VIP")
print(user.name)     # → "김윤섭" (점 표기법, IDE 자동완성 가능)
print(user.nane)     # ← IDE가 빨간 줄로 오타 표시!
# user.age = 31      # ← 에러! NamedTuple은 불변

# 튜플이므로 언패킹 가능
name, age, tier = user
```

```python
# ✅ Good 옵션 2: TypedDict — 타입이 지정된 딕셔너리
from typing import TypedDict

class OrderSummary(TypedDict):
    order_id: str
    total: int
    is_paid: bool

order: OrderSummary = {
    "order_id": "ORD-001",
    "total": 150_000,
    "is_paid": True,
}
# dict처럼 쓰지만, IDE가 키 이름과 값 타입을 검증
print(order["order_id"])   # ✅ 자동완성 가능
print(order["ordr_id"])    # ← mypy가 오타를 잡아줌
```

**언제 뭘 쓰나?**

| 자료구조 | 변경 가능 | dict 호환 | 주 용도 |
|----------|----------|-----------|---------|
| `NamedTuple` | ❌ 불변 | ❌ | 좌표, 설정값 등 변하지 않는 데이터 |
| `TypedDict` | ✅ 가변 | ✅ | JSON 응답, API 페이로드 등 dict 형태가 필요할 때 |
| `dataclass` | ✅ 가변 (기본) | ❌ | 메서드가 필요한 도메인 객체 (Phase 4에서 상세) |
| `Pydantic BaseModel` | ✅ 가변 | ✅ (`.model_dump()`) | 검증이 필요한 외부 입력 (Phase 4에서 상세) |

---

### 2-7. 뮤터블 기본 인자 함정 — Python 최대 함정

```python
# ❌ Bad: 뮤터블 객체를 기본 인자로 사용
def add_item(item: str, cart: list[str] = []) -> list[str]:
    cart.append(item)
    return cart

# 첫 번째 호출
print(add_item("노트북"))   # → ["노트북"] ← 정상
# 두 번째 호출
print(add_item("마우스"))   # → ["노트북", "마우스"] ← ???
# 세 번째 호출
print(add_item("키보드"))   # → ["노트북", "마우스", "키보드"] ← ???

# 왜? 기본 인자 []는 함수가 정의될 때 딱 한 번만 생성됨.
# 모든 호출이 같은 리스트 객체를 공유함!
```

```python
# ✅ Good: None을 기본값으로 쓰고, 함수 안에서 새 리스트 생성
def add_item(item: str, cart: list[str] | None = None) -> list[str]:
    if cart is None:
        cart = []           # 호출할 때마다 새 리스트 생성
    cart.append(item)
    return cart

print(add_item("노트북"))   # → ["노트북"]
print(add_item("마우스"))   # → ["마우스"] ← 매번 독립적!
```

> 💡 **뮤터블 기본 인자 함정**: list `[]`, dict `{}`, set `set()`을 함수의 기본 인자로 쓰면 안 됨.
> Python은 함수가 **정의되는 시점에** 기본값 객체를 한 번만 만들고 재사용하기 때문.
> **규칙**: 뮤터블 기본값은 항상 `None`으로 하고, 함수 안에서 새로 생성.

---

### 2-8. dict 패턴 모음 — 실무에서 자주 쓰는 것들

```python
products = {
    "P001": {"name": "노트북", "price": 1_200_000, "category": "전자기기"},
    "P002": {"name": "마우스", "price": 35_000, "category": "주변기기"},
    "P003": {"name": "키보드", "price": 89_000, "category": "주변기기"},
}

# ── 패턴 1: .get()으로 안전한 접근 ──
# ❌ Bad
price = products["P999"]["price"]       # KeyError!

# ✅ Good
price = products.get("P999", {}).get("price", 0)  # → 0 (안전)

# ── 패턴 2: dict에서 여러 키 한번에 추출 ──
# ❌ Bad
name = products["P001"]["name"]
price = products["P001"]["price"]

# ✅ Good: operator.itemgetter 또는 언패킹
from operator import itemgetter

get_name_price = itemgetter("name", "price")
name, price = get_name_price(products["P001"])
# → ("노트북", 1200000)

# ── 패턴 3: dict 키/값 뒤집기 ──
category_map = {"전자기기": "ELEC", "주변기기": "PERI"}
code_to_name = {v: k for k, v in category_map.items()}
# → {"ELEC": "전자기기", "PERI": "주변기기"}

# ── 패턴 4: 여러 dict에서 동일 키 집계 ──
monthly_revenue = [
    {"month": "1월", "online": 5000, "offline": 3000},
    {"month": "2월", "online": 6000, "offline": 2800},
    {"month": "3월", "online": 7000, "offline": 3200},
]

totals = {
    row["month"]: row["online"] + row["offline"]
    for row in monthly_revenue
}
# → {"1월": 8000, "2월": 8800, "3월": 10200}

# ── 패턴 5: 조건부 키 포함 (** 언패킹 활용) ──
def build_api_payload(
    query: str,
    limit: int = 10,
    offset: int | None = None,
) -> dict[str, str | int]:
    return {
        "query": query,
        "limit": limit,
        **({"offset": offset} if offset is not None else {}),
    }

build_api_payload("노트북")           # → {"query": "노트북", "limit": 10}
build_api_payload("노트북", offset=20) # → {"query": "노트북", "limit": 10, "offset": 20}
```

---

### 2-9. `match-case`로 자료구조 분해하기 (Python 3.10+)

```python
# ❌ Bad: 중첩 if/elif로 데이터 구조 분기
def process_event(event: dict) -> str:
    event_type = event.get("type")
    if event_type == "purchase":
        amount = event.get("amount", 0)
        if amount > 100_000:
            return f"고액 구매: ₩{amount:,}"
        return f"구매: ₩{amount:,}"
    elif event_type == "refund":
        reason = event.get("reason", "미지정")
        return f"환불 ({reason})"
    elif event_type == "page_view":
        page = event.get("page", "/")
        return f"페이지뷰: {page}"
    else:
        return f"알 수 없는 이벤트: {event_type}"
```

```python
# ✅ Good: match-case로 구조적 패턴 매칭
def process_event(event: dict[str, str | int]) -> str:
    match event:
        # dict 구조를 직접 매칭 + 값 추출
        case {"type": "purchase", "amount": int(amount)} if amount > 100_000:
            return f"고액 구매: ₩{amount:,}"

        case {"type": "purchase", "amount": int(amount)}:
            return f"구매: ₩{amount:,}"

        case {"type": "refund", "reason": str(reason)}:
            return f"환불 ({reason})"

        case {"type": "refund"}:   # reason 키가 없는 경우
            return "환불 (미지정)"

        case {"type": "page_view", "page": str(page)}:
            return f"페이지뷰: {page}"

        case {"type": str(unknown_type)}:
            return f"알 수 없는 이벤트: {unknown_type}"

        case _:                    # 어떤 패턴에도 안 맞을 때 (default)
            return "잘못된 이벤트 형식"

# 사용
process_event({"type": "purchase", "amount": 250_000})
# → "고액 구매: ₩250,000"

process_event({"type": "refund", "reason": "사이즈 불일치"})
# → "환불 (사이즈 불일치)"
```

> 💡 **match-case (3.10+)**는 단순 값 비교가 아니라 **구조적 패턴 매칭(structural pattern matching)**.
> dict의 키-값 구조, 리스트의 원소 패턴, 클래스의 속성을 한 번에 분해(destructure)할 수 있음.
> if/elif 체인보다 "이 데이터가 이런 구조면 이렇게 처리"라는 의도가 훨씬 명확.

**match-case로 리스트 구조 매칭:**

```python
def describe_trend(values: list[int | float]) -> str:
    """최근 지표 추세를 한 줄로 요약한다."""
    match values:
        case []:
            return "데이터 없음"

        case [single]:
            return f"단일 값: {single:,}"

        case [first, second] if first < second:
            return f"상승: {first:,} → {second:,}"

        case [first, second]:
            return f"하락/유지: {first:,} → {second:,}"

        case [first, *_, last] if first < last:
            return f"상승 추세: {first:,} → ... → {last:,} ({len(values)}개 포인트)"

        case [first, *_, last]:
            return f"하락 추세: {first:,} → ... → {last:,} ({len(values)}개 포인트)"

describe_trend([100, 120, 150, 180])
# → "상승 추세: 100 → ... → 180 (4개 포인트)"
```

---
