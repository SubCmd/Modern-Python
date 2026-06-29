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

## 2-2. 모던 타입힌트 - `\|` 유니온 (Python 3.10+)

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

## 2-4. f-string 기초 → 고급

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
