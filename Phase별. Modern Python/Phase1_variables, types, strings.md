# Phase 1: 변수·타입·문자열 재정립

> **목표**: "일단 돌아가니까 타입 안 써도 되지?" →
> "타입힌트가 있어야 IDE가 도와주고, 버그가 줄고, FastAPI/Pydantic이 제대로 작동한다"
> **ROI**: ⭐ S등급 — 타입힌트는 FastAPI/Pydantic 생태계의 기반이자, IDE 자동완성 품질을 결정
> **Python 버전**: 3.10+ (Union 축약 `|`), 3.12+ (`type` 문)

---

## 1. 핵심 개념 정리

### 1-1. Python의 타입 시스템 - "동적 타입"이 뭔데?

Python은 **동적 타입 언어(dynamically typed language)**임.
이건 "변수를 만들 때 타입을 안 적어도 된다"라는 의미가 아니라,
**"실행 시점(runtime)에 타입이 결정된다"**는 뜻임.

```python
# Python: 실행 시점에 타입이 결정됨
revenue = 1000        # 이 줄이 실행될 때 int로 결정
revenue = "천원"      # 같은 변수가 str로 바뀜 → 에러 안 남 (동적 타입)

# Java/TypeScript: 코드를 컴파일할 때 타입이 고정됨
# int revenue = 1000;
# revenue = "천원";   // ❌ 컴파일 에러
```

> **문제**
> 동적 타입은 자유롭지만, 코드가 커지면 "이 변수에 뭐가 들어있지?"를 추적하기 어려워짐.
> **타입힌트(type hint)**를 쓰는 이유

---

### 1-2. 타입힌트 = 실행에 영향 없는 "메모"

```python
def calculate_ltv(revenue: float, churn_rate: float) -> float:
    ...
```

여기서 `: float`과 `-> float`은 Python이 **실행할 때 완전히 무시**한다.
그러면 왜 쓰는가?

| 이점 | 설명 |
|------|------|
| **IDE 자동완성** | Cursor/VSCode가 `revenue.`을 눌렀을 때 float 메서드를 보여줌 |
| **버그 사전 감지** | `mypy`가 실행 전에 타입 불일치를 잡아줌 |
| **문서화 효과** | 함수 시그니처만 보고 "아, float 넣고 float 나오는구나" 이해 가능 |
| **FastAPI 연동** | FastAPI가 타입힌트를 읽어서 요청 검증 + Swagger 문서를 자동 생성 |
| **Pydantic 연동** | Pydantic BaseModel의 필드 타입이 곧 타입힌트 |

---

### 1-3. 용어 풀이

| 용어 | 쉬운 설명 |
|------|-----------|
| **타입힌트 (type hint)** | 변수나 함수에 "이건 이런 타입이야"라고 적는 주석. Python이 실행할 때는 무시하지만, IDE와 mypy가 읽음 |
| **타입 추론 (type inference)** | 값을 보고 타입을 자동으로 알아내는 것. `x = 42`이면 IDE가 "x는 int겠구나" 추론 |
| **제네릭 (generic)** | "어떤 타입이든 들어올 수 있다"를 표현하는 방법. `list[int]`는 "int를 담는 리스트" |
| **유니온 (union)** | "이것 또는 저것" 타입. `int \| str`은 "int 아니면 str" |
| **Optional** | "이 값 또는 None". `Optional[str]`은 `str \| None`과 같음 |
| **walrus operator (`:=`)** | 바다코끼리 연산자. 값을 변수에 대입하면서 동시에 그 값을 사용 |
| **f-string** | `f"이름: {name}"` 형태의 문자열. 중괄호 안에 변수나 표현식을 직접 넣음 |
| **리터럴 (literal)** | 코드에 직접 적은 값. `42`, `"hello"`, `[1, 2, 3]`이 리터럴 |

---

## 2. Good vs. Bad 예시

### 2-1. 기본 타입힌트 - 변수와 함수

```python
# ❌ Bad: 타입힌트 없음
def get_user_segment(total_purchase, last_order_days):
    if total_purchase > 1000000 and last_order_days < 30:
        return "VIP"
    elif total_purchase > 500000:
        return "Gold"
    return "Normal"

# 문제점:
# 1. total_purchase가 int인지 float인지? 원(KRW) 단위인지 천원 단위인지?
# 2. last_order_days가 int인지? 음수가 올 수 있는지?
# 3. 반환값이 str인데, 어떤 문자열이 가능한지?
# 4. IDE가 매개변수 타입을 모르니 자동완성 품질이 떨어짐
```

```python
# ✅ Good: 타입힌트 + 의도를 명확히
def get_user_segment(total_purchase: int, last_order_days: int) -> str:
    """유저의 총 구매금액(원)과 마지막 주문 경과일로 세그먼트를 분류한다."""
    if total_purchase > 1_000_000 and last_order_days < 30:
        return "VIP"
    elif total_purchase > 500_000:
        return "Gold"
    return "Normal"

# 개선점:
# 1. int라는 것이 시그니처에 명시 → IDE 자동완성 활성화
# 2. 1_000_000 → 숫자 구분자로 가독성 향상 (Python 3.6+)
# 3. docstring에 "원 단위"라는 비즈니스 맥락까지 기록
```

> 💡 **숫자 구분자 `_`**: `1_000_000`과 `1000000`은 완전히 동일한 값.
> Python이 `_`를 무시하고 숫자만 읽음. 사람이 읽기 쉬우라고 쓰는 것.

---

### 2-2. 모던 타입힌트 - `\|` 유니온 (Python 3.10+)

```python
# ❌ Bad: Python 3.9 이전 스타일
from typing import Optional, Union, List, Dict, Tuple

def search_products(
    query: str,
    category: Optional[str] = None,
    price_range: Optional[Tuple[int, int]] = None,
) -> Union[List[Dict[str, Union[str, int, float]]], None]:
    ...

# 문제점: typing 모듈에서 대문자 타입(List, Dict, Tuple)을 import하는 구식 스타일
# Union과 Optional이 중첩되면 가독성이 급격히 떨어짐
```

```python
# ✅ Good: Python 3.10+ 스타일
def search_products(
    query: str,
    category: str | None = None,
    price_range: tuple[int, int] | None = None,
) -> list[dict[str, str | int | float]] | None:
    ...

# 개선점:
# 1. Optional[X] → X | None (더 직관적)
# 2. Union[X, Y] → X | Y (읽기 쉬움)
# 3. List → list, Dict → dict, Tuple → tuple (소문자 빌트인 사용)
# 4. from typing import ... 줄이 사라짐 (import 감소)
```

> 💡 **Python 3.10의 `|` 문법**:
> 이전에는 "A 또는 B 타입"을 `Union[A, B]`로 적었는데,
> 3.10부터 `A | B`로 줄여 쓸 수 있음. `Optional[X]`는 `X | None`과 완전히 동일.

**버전별 타입힌트 표기 비교:**

| 표현 | 3.9 이전 | 3.10+ |
|------|----------|-------|
| A 또는 B | `Union[A, B]` | `A \| B` |
| A 또는 None | `Optional[A]` | `A \| None` |
| 정수 리스트 | `List[int]` | `list[int]` |
| 문자열→정수 딕셔너리 | `Dict[str, int]` | `dict[str, int]` |
| 정수 2개 튜플 | `Tuple[int, int]` | `tuple[int, int]` |

---

### 2-3. `type` 문으로 타입 별칭 만들기 (Python 3.12+)

```python
# ❌ Bad: 복잡한 타입을 매번 반복
def get_cohort_retention(
    start_date: str,
    end_date: str,
) -> dict[str, list[dict[str, int | float | None]]]:
    ...

def export_cohort_data(
    data: dict[str, list[dict[str, int | float | None]]],
    format: str = "csv",
) -> None:
    ...

# 문제점: dict[str, list[dict[str, int | float | None]]]을 두 번 반복
# 실수로 하나만 수정하면 불일치 발생
```

```python
# ✅ Good (3.10~3.11): TypeAlias로 별칭
from typing import TypeAlias

CohortRow: TypeAlias = dict[str, int | float | None]
CohortData: TypeAlias = dict[str, list[CohortRow]]

def get_cohort_retention(start_date: str, end_date: str) -> CohortData:
    ...

def export_cohort_data(data: CohortData, format: str = "csv") -> None:
    ...
```

```python
# ✅✅ Best (3.12+): type 문 사용
type CohortRow = dict[str, int | float | None]
type CohortData = dict[str, list[CohortRow]]

def get_cohort_retention(start_date: str, end_date: str) -> CohortData:
    ...

def export_cohort_data(data: CohortData, format: str = "csv") -> None:
    ...

# 개선점:
# 1. from typing import TypeAlias가 필요 없음
# 2. type 키워드가 "이건 타입 별칭이야"라고 명확히 선언
# 3. IDE와 mypy가 더 정확하게 추론 가능
```

> 💡 **`type` 문 (3.12+)**:
> `type CohortRow = ...`는 단순한 변수 대입이 아니라,
> Python에게 "이건 타입 별칭이야"라고 공식적으로 알려주는 전용 문법.
> 기존 `TypeAlias`는 "힌트"에 불과했지만, `type` 문은 언어 차원의 지원.

---

### 2-4. f-string 기초 → 고급

```python
# ❌ Bad: 구식 문자열 포매팅
user_name = "윤섭"
order_count = 42
revenue = 1_580_000

# 방법 1: % 포매팅 (C 스타일, Python 2 시절)
msg = "%s님의 주문 %d건, 매출 %d원" % (user_name, order_count, revenue)

# 방법 2: .format() (Python 3 초기)
msg = "{}님의 주문 {}건, 매출 {}원".format(user_name, order_count, revenue)

# 문제점: 변수와 위치를 매칭하기 어렵고, 변수가 많아지면 실수하기 쉬움
```

```python
# ✅ Good: f-string (Python 3.6+)
msg = f"{user_name}님의 주문 {order_count}건, 매출 {revenue:,}원"
# → "윤섭님의 주문 42건, 매출 1,580,000원"

# 개선점:
# 1. 변수 이름이 문자열 안에 직접 보임 → 가독성 최고
# 2. {:,}로 천 단위 콤마 자동 삽입
# 3. 변수 순서 실수 없음 (위치 기반이 아니라 이름 기반)
```

---

### 2-5. f-string 고급 기능

#### (a) `=` 셀프 문서화 (Python 3.8+, 디버깅 특화)

```python
# ❌ Bad: 디버깅할 때 변수명과 값을 따로 적음
total = 150_000
discount_rate = 0.15
final = total * (1 - discount_rate)
print(f"total: {total}, discount_rate: {discount_rate}, final: {final}")
# → "total: 150000, discount_rate: 0.15, final: 127500.0"
```

```python
# ✅ Good: f-string에 = 붙이기 (셀프 문서화)
total = 150_000
discount_rate = 0.15
final = total * (1 - discount_rate)
print(f"{total=}, {discount_rate=}, {final=}")
# → "total=150000, discount_rate=0.15, final=127500.0"

# 표현식에도 사용 가능
print(f"{total * (1 - discount_rate) = :,.0f}")
# → "total * (1 - discount_rate) = 127,500"
```

> 💡 **`=` 기능**: f-string 안에서 `{변수=}`라고 쓰면
> **변수명 = 값** 형태로 자동 출력. 디버깅할 때 `print(f"x: {x}")`보다 훨씬 빠름.


#### (b) 포맷 스펙 (숫자, 정렬, 날짜)

```python
revenue = 15832400
conversion_rate = 0.0347
from datetime import datetime
now = datetime.now()

# 숫자 포매팅
print(f"매출: {revenue:>15,}원")       # 오른쪽 정렬, 15칸, 천 단위 콤마
# → "매출:      15,832,400원"

print(f"전환율: {conversion_rate:.1%}")  # 퍼센트 변환 (소수점 1자리)
# → "전환율: 3.5%"

print(f"전환율: {conversion_rate:.4f}") # 소수점 4자리 고정
# → "전환율: 0.0347"

# 날짜 포매팅
print(f"보고서 생성: {now:%Y-%m-%d %H:%M}")
# → "보고서 생성: 2026-06-29 14:30"

# 진법 변환
user_id = 255
print(f"User ID: {user_id:#x}")  # 16진수
# → "User ID: 0xff"
print(f"권한 비트: {user_id:#b}")  # 2진수
# → "권한 비트: 0b11111111"
```

**자주 쓰는 포맷 스펙 요약:**

| 스펙 | 의미 | 예시 | 결과 |
|------|------|------|------|
| `:,` | 천 단위 콤마 | `f"{1234567:,}"` | `"1,234,567"` |
| `:.2f` | 소수점 2자리 고정 | `f"{3.14159:.2f}"` | `"3.14"` |
| `:.1%` | 퍼센트 (소수점 1자리) | `f"{0.0347:.1%}"` | `"3.5%"` |
| `:>10` | 오른쪽 정렬, 10칸 | `f"{'hi':>10}"` | `"        hi"` |
| `:<10` | 왼쪽 정렬, 10칸 | `f"{'hi':<10}"` | `"hi        "` |
| `:^10` | 가운데 정렬, 10칸 | `f"{'hi':^10}"` | `"    hi    "` |
| `:0>5` | 0으로 채우기 | `f"{42:0>5}"` | `"00042"` |


#### (c) f-string 안의 중첩 표현식 (Python 3.12+)

```python
# Python 3.12 이전: f-string 안에서 같은 따옴표 사용 불가
# ❌ Bad
# name = f"{'VIP' if score > 100 else 'Normal'}"  # 작동은 하지만 가독성 나쁨

# Python 3.12+: f-string 안에서 자유로운 표현식 허용
users = {"김윤섭": "VIP", "이민수": "Gold"}

# ✅ Good (3.12+)
print(f"세그먼트: {users["김윤섭"]}")  # f-string 안에서 큰따옴표 재사용 가능
# → "세그먼트: VIP"

# 3.12 이전에는 이렇게 해야 했음:
print(f"세그먼트: {users['김윤섭']}")  # 안쪽에 작은따옴표 써야 함
```

> 💡 **3.12 f-string 개선**: 이전에는 f-string 바깥의 따옴표와 안쪽 따옴표가
> 겹치면 에러가 났는데, 3.12부터는 중첩 제한이 풀림.

---

### 2-6. walrus operator `:=` (바다코끼리 연산자, Python 3.8+)

```python
# ❌ Bad: 값을 계산하고, 조건문에서 다시 사용하려면 변수를 미리 만들어야 함
import re

# 예시 1: 정규식 매치
line = "Order #12345 - Total: 150,000원"
match = re.search(r"Order #(\d+)", line)
if match:
    order_id = match.group(1)
    print(f"주문번호: {order_id}")

# 예시 2: 리스트에서 조건 필터링 후 변환
raw_revenues = ["100000", "invalid", "250000", "N/A", "180000"]
valid = []
for r in raw_revenues:
    stripped = r.strip()
    if stripped.isdigit():
        valid.append(int(stripped))
```

```python
# ✅ Good: walrus operator로 대입과 사용을 한 줄에
import re

# 예시 1: 정규식 매치 — 대입과 조건 판단을 동시에
line = "Order #12345 - Total: 150,000원"
if match := re.search(r"Order #(\d+)", line):
    print(f"주문번호: {match.group(1)}")
# match 변수가 None이 아닐 때만 if 블록 진입

# 예시 2: 리스트 컴프리헨션에서 중간 계산 결과 재사용
raw_revenues = ["100000", "invalid", "250000", "N/A", "180000"]
valid = [
    int(stripped)
    for r in raw_revenues
    if (stripped := r.strip()).isdigit()
]
# → [100000, 250000, 180000]
# stripped를 한 번만 계산하고, 조건 판단 + 변환에 모두 사용
```

> 💡 **walrus operator `:=`**:
> 일반 `=`은 "대입문(statement)"이라 if/while 조건 안에서 못 쓴다.
> `:=`은 "대입 표현식(expression)"이라 조건 안에서 값을 대입하면서 동시에 그 값을 반환.
> 이름의 유래: `:=` 모양이 바다코끼리 눈과 엄니를 닮아서.


**walrus가 유용한 대표 패턴 3가지:**

```python
# 패턴 1: while + 입력 읽기
while (line := input("쿼리 입력 (q=종료): ")) != "q":
    print(f"실행: {line}")

# 패턴 2: API 응답에서 값 추출 + None 체크
if (data := response.get("results")) is not None:
    process(data)

# 패턴 3: 비용이 큰 함수 호출 결과 재사용
if (result := expensive_query(user_id)) and result.is_valid:
    save(result)
```

---

### 2-7. None 처리 패턴

```python
# ❌ Bad: None 체크를 == 로 함
def get_discount(user_tier):
    if user_tier == None:      # ❌ == 대신 is 사용해야 함
        return 0
    if user_tier == "VIP":
        return 0.2
    return 0.05

# 더 나쁜 예: None을 빈 문자열이나 0과 혼동
def get_display_name(name):
    if not name:               # ❌ 빈 문자열 ""도 False, 0도 False
        return "Unknown"       # name이 0이나 ""일 때도 Unknown 반환됨
    return name
```

```python
# ✅ Good: None은 항상 is / is not으로 비교
def get_discount(user_tier: str | None) -> float:
    if user_tier is None:      # ✅ is None (동일 객체인지 비교)
        return 0.0
    if user_tier == "VIP":
        return 0.2
    return 0.05

# None과 falsy 값을 명확히 구분
def get_display_name(name:str | None) -> str:
    if name is None:           # ✅ None만 체크 (빈 문자열은 통과)
        return "Unknown"
    return name

# 또는 더 간결하게 (기본값 패턴)
def get_display_name(name: str | None) -> str:
    return name if name is not None else "Unknown"
```

> 💡 **`is` vs `==`**:
> - `==`는 **값이 같은지** 비교 (내용 비교)
> - `is`는 **같은 객체인지** 비교 (메모리 주소 비교)
> - None은 Python 전체에서 딱 하나만 존재하는 특별한 객체(싱글톤)이므로 `is`가 정확

**None 관련 Falsy 함정 정리:**

```python
# Python에서 False로 평가되는 값들 (falsy values):
# None, False, 0, 0.0, "", [], {}, set(), ()

# 이들이 모두 다른 의미인데 if not x로 뭉뚱그리면 버그 발생
value = 0  # 유효한 값 (할인율 0%, 재고 0개 등)
if not value:
    print("값 없음!")  # ❌ 0은 유효한 값인데 "값 없음"으로 처리됨

if value is None:
    print("값 없음!")  # ✅ None일 때만 "값 없음"
```

---

### 2-8. 문자열 메서드 - 알지만 잘 안 쓰는 것들

```python
# ❌ Bad: 수동으로 문자열 조작
tags = ["프로모션", "여름세일", "신규회원"]
tag_string = ""
for i, tag in enumerate(tags):
    tag_string += tag                   # 문자열 += 반복은 성능 나쁨
    if i < len(tags) - 1:
        tag_string += ", "
# → "프로모션, 여름세일, 신규회원"
```

```python
# ✅ Good: str.join()
tags = ["프로모션", "여름세일", "신규회원"]
tag_string = ", ".join(tags)
# → "프로모션, 여름세일, 신규회원"
```

```python
# 실전에서 자주 쓰이는 str 메서드 모음

order_id = "  ORD-2024-00123  "

# 1. strip 계열: 양쪽/왼쪽/오른쪽 공백(또는 특정 문자) 제거
order_id.strip()             # → "ORD-2024-00123"
order_id.lstrip()            # → "ORD-2024-00123  " (왼쪽만)
"###VIP###".strip("#")       # → "VIP" (특정 문자 제거)

# 2. startswith / endswith: 접두사/접미사 체크 (여러 개 가능)
filename = "report_2024.csv"
filename.endswith((".csv", ".tsv", ".xlsx"))  # → True (튜플로 여러 확장자 체크)

# 3. removeprefix / removesuffix (Python 3.9+)
"test_calculate_ltv".removeprefix("test_")   # → "calculate_ltv"
"report.csv".removesuffix(".csv")            # → "report"
# ❌ 이전에는 이렇게 해야 했음:
# s[len("test_"):] if s.startswith("test_") else s

# 4. partition: 구분자 기준으로 3분할
"user_id=12345".partition("=")  # → ("user_id", "=", "12345")
# split과 다르게 구분자도 반환 + 정확히 3개로만 분할

# 5. zfill: 0으로 채우기
"42".zfill(5)                   # → "00042" (주문번호 포매팅)
```

---

### 2-9. 변수 네이밍 - 의도를 드러내는 이름

```python
# ❌ Bad: 축약어, 의미 불명확한 이름
def calc(d, r):
    return d * (1 - r)

t = 30
ul = ["김윤섭", "이민수"]
flag = True
tmp = get_data()
```

```python
# ✅ Good: 의도를 드러내는 이름
def calculate_discounted_prcie(original_price: int, discount_rate: float) -> float:
    return original_price * (1 - discount_rate)

retention_days: int = 30
active_user_names: list[str] = ["김윤섭", "이민수"]
is_premium_user: bool = True        # bool은 is_, has_, can_ 접두사
daily_revenue_data = get_data()     # "이게 뭔 데이터?"가 아니라 "일별 매출 데이터"
```

**Python 네이밍 컨벤션 (PEP 8):**

| 대상 | 스타일 | 예시 |
|------|--------|------|
| 변수, 함수, 메서드 | snake_case | `user_count`, `calculate_ltv()` |
| 클래스 | PascalCase | `UserSegment`, `OrderProcessor` |
| 상수 | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT`, `DEFAULT_TIMEOUT` |
| 비공개(내부용) | `_` 접두사 | `_internal_cache`, `_validate()` |
| bool 변수 | `is_`, `has_`, `can_` 접두사 | `is_active`, `has_discount` |

---

## 3. 실전 예제: 이커머스 분석 함수 리팩터링

### 3-1. Before (타입힌트 없음, 구식 문법)

```python
# ❌ Before: growth_metrics.py (구식 스타일)

from typing import Optional, List, Dict, Tuple

def analyze_funnel(events, target_event=None):
    results = {}
    total = len(events)
    if total == 0:
        return None

    for e in events:
        step = e.get("step", "unknown")
        if step not in results:
            results[step] = 0
        results[step] += 1

    output = []
    for step, count in results.items():
        rate = count / total * 100
        row = {
            "step": step,
            "count": count,
            "rate": "%.1f%%" % rate,    # % 포매팅
        }
        if target_event != None:    # == None
            if step == target_event:
                row["is_target"] = True
        output.append(row)

    return output
```

### 3-2. After (모던 Python)

```python
# ✅ After: growth_metrics.py (모던 스타일)
from collections import Counter
from tkinter import NO

type FunnelEvent = dict[str, str | int]
type FunnelRow = dict[str, str | int | float | bool]

def analyze_funnel(
    events: list[FunnelEvent],
    target_event: str | None = None,
) -> list[FunnelRow] | None:
    f"""퍼널 이벤트 목록을 받아 단계별 전환율을 계산한다.

    Args:
        events: 각 이벤트는 {"step": "장바구니", "user_id": 123} 형태.
        target_event: 하이라이트할 특정 단계. None이면 전체 표시.

    Returns:
        단계별 카운트 + 전환율 리스크. 이벤트가 비어있으면 None.
    """
    if not events:
        return None

    total = len(events)
    step_counts = Counter(event.get("step", "unknown") for event in events)

    return [
        {
            "step": step,
            "count": count,
            "rate": f"{count / total:.1%}",          # f-string + :.1%
            **({"is_target": True}                    # 조건부 dict 병합
               if target_event is not None and step == target_event
               else {}),
        }
        for step, count in step_counts.items()
    ]
```

**변경 포인트 정리:**

| # | Before | After | 이유 |
|---|--------|-------|------|
| 1 | `from typing import ...` | `type` 문 (3.12+) | import 감소, 명시적 별칭 |
| 2 | `Optional[str]` | `str \| None` | 가독성 향상 |
| 3 | 수동 dict counting | `Counter` | 표준 라이브러리 활용 |
| 4 | `"%.1f%%" % rate` | `f"{count / total:.1%}"` | f-string이 더 읽기 쉬움 |
| 5 | `!= None` | `is not None` | 정확한 None 비교 |
| 6 | 반복문 + append | 리스트 컴프리헨션 | Pythonic한 패턴 (Phase 2에서 상세 다룸) |
| 7 | 조건부 dict 키 추가 | `**({...} if ... else {})` | dict 언패킹으로 조건부 필드 |

---
