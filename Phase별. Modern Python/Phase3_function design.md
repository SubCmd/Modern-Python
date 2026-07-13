# Phase 3: 함수 설계 원칙

> **목표**: "일단 def 만들어서 돌리는" 수준에서 →
> "데코레이터를 직접 만들고, FastAPI/LangChain 내부 구조가 왜 그런지 읽히는" 수준으로
> **ROI**: ⭐ S등급 — 데코레이터·클로저는 FastAPI(`@app.get`), pytest(`@fixture`), LangChain(`@tool`) 등 Python 생태계 전반의 기반 패턴

---

## 1. 핵심 개념 정리

### 1-1. 이 Phase에서 다루는 것들의 관계

```
일급 함수 (함수를 값처럼 다룸)
    │
    ├── 함수를 변수에 담기
    ├── 함수를 인자로 넘기기  ──→  sorted(key=...), map(), filter()
    └── 함수를 반환하기      ──→  클로저 (외부 변수를 기억하는 함수)
                                     │
                                     └── 데코레이터 (함수를 받아서 "기능이 추가된 함수"를 반환)
                                            │
                                            ├── @app.get("/")     ← FastAPI
                                            ├── @pytest.fixture   ← pytest
                                            ├── @tool             ← LangChain
                                            └── @lru_cache        ← functools
```

### 1-2. 용어 풀이

| 용어 | 쉬운 설명 |
|------|-----------|
| **일급 함수 (first-class function)** | 함수를 숫자나 문자열처럼 변수에 담고, 다른 함수에 넘기고, 반환할 수 있는 성질 |
| **고차 함수 (higher-order function)** | 함수를 인자로 받거나 함수를 반환하는 함수. `sorted(key=func)`, `map(func, items)` |
| **클로저 (closure)** | 바깥 함수가 끝난 뒤에도, 바깥 함수의 변수를 기억하고 사용하는 안쪽 함수 |
| **데코레이터 (decorator)** | 기존 함수를 수정하지 않고, 추가 기능을 감싸서 붙이는 패턴. `@데코레이터` 문법 |
| **`*args`** | 위치 인자(positional arguments)를 튜플로 모아 받는 문법 |
| **`**kwargs`** | 키워드 인자(keyword arguments)를 딕셔너리로 모아 받는 문법 |
| **키워드 전용 인자** | `*` 뒤에 오는 매개변수. 반드시 `이름=값` 형태로만 전달 가능 |
| **위치 전용 인자** | `/` 앞에 오는 매개변수. 반드시 위치로만 전달 가능 (Python 3.8+) |
| **순수 함수 (pure function)** | 같은 입력이면 항상 같은 출력. 외부 상태를 바꾸지 않는 함수 |

---

## 2. Good vs Bad 예시

### 2-1. 함수 시그니처 설계 — `/`와 `*`

```python
# ❌ Bad: 어떤 인자를 위치로 넘길지, 키워드로 넘길지 모호
def calculate_revenue(amount, tax_rate, discount_rate, currency):
    net = amount * (1 + tax_rate) * (1 - discount_rate)
    return f"{currency} {net:,.0f}"

# 이렇게도 호출 가능하고
calculate_revenue(100_000, 0.1, 0.05, "KRW")
# 이렇게도 호출 가능 → 혼란
calculate_revenue(currency="KRW", amount=100_000, tax_rate=0.1, discount_rate=0.05)
# 이것도 가능 → 더 혼란
calculate_revenue(100_000, 0.1, currency="KRW", discount_rate=0.05)
```

```python
# ✅ Good: / 와 * 로 호출 방식을 강제
def calculate_revenue(
    amount: int,           # ← / 앞: 위치로만 전달 가능
    /,
    tax_rate: float,       # ← / 와 * 사이: 위치 또는 키워드 둘 다 가능
    *,
    discount_rate: float = 0.0,  # ← * 뒤: 키워드로만 전달 가능
    currency: str = "KRW",
) -> str:
    net = amount * (1 + tax_rate) * (1 - discount_rate)
    return f"{currency} {net:,.0f}"

# [ 구역 1] / [구역 2] * [구역 3]
# 위치 전용 / 위치 & 키워드 * 키워드 전용
# 순서대로만 / 둘 다 가능 * 이름=값으로만

# ✅ 허용
calculate_revenue(100_000, 0.1, discount_rate=0.05)
calculate_revenue(100_000, tax_rate=0.1, discount_rate=0.05, currency="USD")

# ❌ 에러: amount는 위치 전용
calculate_revenue(amount=100_000, tax_rate=0.1)  # TypeError!

# ❌ 에러: discount_rate는 키워드 전용
calculate_revenue(100_000, 0.1, 0.05)  # TypeError!
```

> 💡 **`/`와 `*`의 역할**:
> ```
> def func(a, b, /, c, d, *, e, f):
>          ^^^^      ^^^^      ^^^^
>       위치 전용     자유    키워드 전용
> ```
> - `/` 앞: 위치로만 전달 (이름으로 지정 불가)
> - `/`와 `*` 사이: 위치도 키워드도 OK (기본 동작)
> - `*` 뒤: 키워드로만 전달 (위치로 지정 불가)
>
> **왜 쓰나?**
> API를 설계할 때 "이 인자는 이름을 바꿀 수도 있으니 위치로만 쓰게 하자"(`/`),
> "이 인자는 뭔지 명확히 알아야 하니 이름을 꼭 쓰게 하자"(`*`)로 의도를 강제.

**실전 활용 — FastAPI에서 `*`가 쓰이는 이유:**

```python
from fastapi import FastAPI, Query

app = FastAPI()

# FastAPI의 Query()는 기본값 역할을 하면서 동시에 검증 규칙을 정의
# * 뒤의 키워드 전용 인자로 설계되어 있음
@app.get("/products")
async def search_products(
    *,                                   # ← 이후 모든 인자를 키워드 전용으로
    query: str = Query(min_length=1),
    category: str | None = None,
    min_price: int = Query(default=0, ge=0),
    limit: int = Query(default=20, le=100),
):
    ...
```

---

### 2-2. `*args`와 `**kwargs` - 정확한 용도

```python
# ❌ Bad: 무분별한 *args, **kwargs 남용
def create_user(*args, **kwargs):
    # args[0]이 뭔지, kwargs에 뭐가 오는지 전혀 알 수 없음
    # IDE 자동완성 불가, 문서화 불가
    name = args[0]
    email = args[1]
    age = kwargs.get("age", 0)
    ...

# 호출하는 쪽에서도 시그니처를 알 수 없음
create_user("김윤섭", "kim@email.com", age=30)
```

```python
# ✅ Good: 명시적 매개변수를 먼저, *args/**kwargs는 특수 목적에만
def create_user(
    name: str,
    email: str,
    *,
    age: int = 0,
    tier: str = "Normal",
) -> dict[str, str | int]:
    return {"name": name, "email": email, "age": age, "tier": tier}
```

**`*args`와 `**kwargs`가 정당한 경우:**

```python
# ✅ 용도 1: 래퍼(wrapper) 함수 — 원본 함수의 인자를 그대로 전달
def with_logging(func):
    def wrapper(*args, **kwargs):       # 어떤 함수든 감쌀 수 있으려면
        print(f"호출: {func.__name__}")     # args/kwargs로 모든 인자를 받아야 함.
        return func(*args, **kwargs)
    return wrapper

# ✅ 용도 2: 가변 개수 인자 (동일 타입이 여러 개)
def calculate_total(*amounts: int) -> int:
    """여러 금액의 합계를 계산한다."""
    return sum(amounts)

calculate_total(10_000, 25_000, 5_000)  # → 40000

# ✅ 용도 3: 설정 딕셔너리 전달 (API 호출 등)
def call_llm_api(prompt: str, **model_kwargs: float | int | str) -> str:
    """LLM API 호출. 모델별 파라미터가 다르므로 **kwargs로 받음."""
    # model_kwargs: {"temperature": 0.7, "max_tokens": 1000, ...}
    '''
```

> 💡 **규칙**
> 매개변수 이름을 알고 있으면 명시적으로 적기. `*args`/`**kwargs`는
> "어떤 인자가 올지 미리 알 수 없는 경우"(래퍼, 프록시, 플러그인)에만 사용.

> `*args`와 `**kwargs`를 사용하는 이유?
> 1. 함수의 유연성 및 확장성 극대화 : `*args`, `**kwargs` 인자가 없다면 매번 함수 매개변수를 수정해줘야함.
> 2. 데이터 일괄 처리 : 인자가 여러 개 들어와도 반복문 한 줄로 데이터 처리 가능
> 3. 데코레이터 및 함수 전달 필수품 : 프록시 함수 만들 때 좋다 (받은 인자를 그대로 다른 함수로 넘김)
> 즉,
> `*args` : 몇 개가 들어올지 모르는 값들을 튜플로 묶어 처리
> `**kwargs` : 몇 개가 들어올지 모르는 값들을 딕셔너리로 묶어 처리

---

### 2-3. 일급 함수 - 함수를 값처럼 다루기

```python
# ❌ Bad: 조건마다 비슷한 로직을 복사
def sort_by_revenue(products):
    return sorted(products, key=lambda p: p["revenue"], reverse=True)

def sort_by_conversion(products):
    return sorted(products, key=lambda p: p["conversion_rate"], reverse=True)

def sort_by_name(products):
    return sorted(products, key=lambda p: p["name"])
```

```python
# ✅ Good: 함수를 인자로 넘겨서 전략(strategy)을 외부에서 결정
from typing import Callable

type Product = dict[str, str | int | float]
type SortKey = Callable[[Product], str | int | float]

def sort_products(
    products: list[Product],
    key_func: SortKey,
    *,
    descending: bool = True,
) -> list[Product]:
    """주어진 정렬 기준으로 상품을 정렬한다."""
    return sorted(products, key=key_func, reverse=descending)

# 사용: 정렬 기준을 호출 시점에 결정
products = [
    {"name": "노트북", "revenue": 5_000_000, "conversion_rate": 0.03},
    {"name": "마우스", "revenue": 800_000, "conversion_rate": 0.12},
    {"name": "키보드", "revenue": 1_200_000, "conversion_rate": 0.08},
]

by_revenue = sort_products(products, key_func=lambda p: p["revenue"])
by_cvr = sort_products(products, key_func=lambda p: p["conversion_rate"])
by_name = sort_products(products, key_func=lambda p: p["name"], descending=False)
```


**함수를 딕셔너리에 담아서 디스패치하기:**

```python
# ❌ Bad: if/elif 체인으로 함수 분기
def process_metric(metric_type: str, value: float) -> str:
    if metric_type == "currency":
        return f"₩{value:,.0f}"
    elif metric_type == "rate":
        return f"{value:.1%}"
    elif metric_type == "count":
        return f"{value:,.0f}명"
    else:
        return str(value)
```

```python
# ✅ Good: 함수 디스패치 테이블
type Formatter = Callable[[float], str]

METRIC_FORMATTERS: dict[str, Formatter] = {
    "currency": lambda v: f"₩{v:,.0f}",
    "rate":     lambda v: f"{v:.1%}",
    "count":    lambda v: f"{v:,.0f}명",
}

def process_metric(metric_type: str, value: float) -> str:
    formatter = METRIC_FORMATTERS.get(metric_type, str)
    return formatter(value)

#새 타입 추가가 쉬움 (함수 하나 추가하면 끝)
METRIC_FORMATTERS["duration"] = lambda v: f"{v:.1f}초"
```

> 💡 **함수 디스패치 테이블**
> if/elif 분기 대신 dict에 함수를 담아서, 키로 함수를 꺼내 실행하는 패턴.
> 새로운 분기를 추가할 때 기존 코드를 건드리지 않아도 됨.
> FastAPI의 라우팅(`{"/products": handler_func}`)도 본질적으로 이 패턴.

---

### 2-4. 클로저 — 바깥 변수를 "기억"하는 함수

```python
# 클로저란?
# 바깥 함수(outer)가 끝난 뒤에도,
# 안쪽 함수(inner)가 바깥 함수의 변수를 계속 참조할 수 있는 구조

def make_discount_calculator(discount_rate: float):
    """할인율을 고정한 계산기 함수를 반환한다."""

    # 이 안쪽 함수가 클로저 — discount_rate를 "기억"함
    def calculate(price: int) -> int:
        return int(price * (1 - discount_rate))

    return calculate  # ← 함수 자체를 반환 (호출이 아님!)

# 할인율별 계산기 생성
vip_discount = make_discount_calculator(0.20)    # 20% 할인
gold_discount = make_discount_calculator(0.10)   # 10% 할인

# 사용
vip_discount(100_000)    # → 80000  (discount_rate=0.20이 기억됨)
gold_discount(100_000)   # → 90000  (discount_rate=0.10이 기억됨)

# make_discount_calculator()는 이미 실행이 끝났는데,
# vip_discount 안에서 discount_rate=0.20을 계속 사용할 수 있음
# → 이것이 클로저
```

> 💡 **클로저의 핵심**
> 함수가 **자신이 정의된 환경(scope)의 변수를 기억**하는 것.
> 마치 함수가 "태어난 집의 주소"를 기억하고, 나중에 그 집에 있는 물건을 꺼내 쓰는 것과 비슷.

**클로저의 실전 활용 — 설정 주입:**

```python
# API 키, 모델명 등 설정을 한 번 주입하면, 이후 호출마다 반복 불필요
def create_llm_client(
    model: str = "claude-sonnet-4-6",
    max_tokens: int = 1000,
):
    """설정이 주입된 LLM 호출 함수를 반환한다."""
    def call(prompt: str, *, temperature: float = 0.7) -> str:
        # model, max_tokens는 클로저로 기억됨
        print(f"[{model}] max_tokens={max_tokens}, temp={temperature}")
        print(f"Prompt: {prompt}")
        return f"응답 from {model}"
    return call

# 설정 주입
sonnet = create_llm_client("claude-sonnet-4-6", max_tokens=2000)
haiku = create_llm_client("claude-haiku-4-5-20251001", max_tokens=500)

# 이후 호출 시 model/max_tokens를 매번 적지 않아도 됨
sonnet("매출 분석해줘")          # [claude-sonnet-4-6] max_tokens=2000, temp=0.7
haiku("요약해줘", temperature=0.3) # [claude-haiku-4-5-20251001] max_tokens=500, temp=0.3

'''
[ 1단계: 설정 주입 (공장 가동) ]
create_llm_client("claude-sonnet-4-6", max_tokens=2000)
  │
  ├───► [ 메모리 공간 (배낭) ] ───────┐
  │      model = "claude-sonnet-4-6" │
  │      max_tokens = 2000           │
  │                                  ▼
  └───► 내부 call 함수가 이 배낭을 짊어지고 밖으로 나옴 ──► 변수 'sonnet'에 저장

-------------------------------------------------------------------------

[ 2단계: 실제 사용 (일꾼 호출) ]
sonnet("매출 분석해줘")  # 이제 모델명이나 토큰수를 넘길 필요가 없음!
  │
  └───► 'sonnet' 일꾼이 실행되면서 자기가 메고 있던 배낭에서
        model("claude-sonnet-4-6")과 max_tokens(2000)를 쏙 빼서 사용함.
'''
```

---

### 2-5. 데코레이터(Decorator) - 단계별 이해

데코레이터는 Python에서 가장 중요한 패턴 중 하나. 천천히 단계를 밟아보자!

```python
# 가장 단순한 데코레이터: 실행 시간을 측정
import time

def timer(func):
    """함수 실행 시간을 측정하는 데코레이터."""
    def wrapper(*args, **kwargs):
        start = time.perft_counter()
        result = func(*args, **kwargs)      # 원본 함수 실행
        elapsed = time.peft_counter() - start
        print(f"⏱ {func.__name__}: {elapsed:.4f}초")
        return result
    return wrapper

# 사용법 1: 수동 적용 (데코레이터의 본질)
def slow_query():
    time.sleep(0.5)
    return "결과"

slow_query = timer(slow_query)  # ← 원본을 "강화된 버전"으로 교체
slow_query()                    # ⏱ slow_query: 0.5003초

# 사용법 2: @ 문법 (위와 완전히 동일)
@timer                          # ← slow_query = timer(slow_query)의 축약
def slow_query():
    time.sleep(0.5)
    return "결과"

slow_query()                    # ⏱ slow_query: 0.5003초
```

> 💡 **`@decorator`는 문법적 설탕(syntactic sugar)**.
> `@timer`를 붙이면 Python이 자동으로 `slow_query = timer(slow_query)`를 실행
> 이해의 핵심: **데코레이터는 특별한 문법이 아니라, "함수를 받아서 함수를 반환"하는 고차 함수**


#### Step 2: `functools.wraps` — 원본 함수 정보 보존

```python
# ❌ Bad: wraps 없는 데코레이터
def timer(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"⏱ {func.__name__}: {elapsed:.4f}초")
        return result
    return wrapper

@timer
def analyze_cohort():
    """코호트 분석을 실행한다."""
    ...

print(analyze_cohort.__name__)  # → "wrapper" ← 원본 이름이 사라짐!
print(analyze_cohort.__doc__)   # → None      ← docstring도 사라짐!
```

```python
# ✅ Good: functools.wraps로 원본 정보 보존
from functools import wraps

def timer(func):
    @wraps(func)  # ← 이 한 줄 추가만으로 원본 함수의 메타데이터 보존
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"⏱ {func.__name__}: {elapsed:.4f}초")
        return result
    return wrapper

@timer
def analyze_cohort():
    """코호트 분석을 실행한다."""
    ...

print(analyze_cohort.__name__)  # → "analyze_cohort" ✅
print(analyze_cohort.__doc__)   # → "코호트 분석을 실행한다." ✅
```

> 💡 **`@wraps(func)`**
> wrapper 함수에 원본 함수의 `__name__`, `__doc__`, `__module__` 등을 복사해줌
> **데코레이터를 만들 때 `@wraps`는 필수**. 안 쓰면 디버깅·문서화에서 문제 발생.


#### Step 3: 인자를 받는 데코레이터

```python
# 목표: @retry(max_attempts=3, delay=1.0) 처럼 설정을 넘기고 싶다

# 구조가 한 단계 더 중첩됨:
# retry(max_attempts=3) → "데코레이터 함수"를 반환
#                       → 그 데코레이터가 원본 함수를 받아서 wrapper를 반환

from functools import wraps
import time

def retry(max_attempts: int = 3, delay: float = 1.0):
    """실패 시 재시도하는 데코레이터. 인자로 재시도 횟수와 대기 시간을 받음."""

    def decorator(func):              # ← 실제 데코레이터
        @wraps(func)
        def wrapper(*args, **kwargs): # ← 실제 래퍼
            last_exception = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    print(f"⚠ {func.__name__} 실패 ({attempt}/{max_attempts}): {e}")
                    if attempt < max_attempts:
                        time.sleep(delay)
            raise last_exception   # 모든 재시도 실패 시 마지막 예외를 다시 발생
        return wrapper
    return decorator

# 사용
@retry(max_attempts=3, delay=0.5)
def fetch_analytics_data(campaign_id: str) -> dict:
    """외부 API에서 캠페인 데이터를 가져온다."""
    # 네트워크 오류가 발생할 수 있는 코드
    ...
```

**데코레이터 3단 구조 분해:**

```
@retry(max_attempts=3, delay=0.5)      ← Step 1: retry(...)를 호출 → decorator 반환
def fetch_analytics_data(...):         ← Step 2: decorator(fetch_analytics_data) → wrapper 반환
    ...                                 ← Step 3: 이후 fetch_analytics_data()를 호출하면 wrapper() 실행

# 풀어 쓰면:
decorator = retry(max_attempts=3, delay=0.5)   # 바깥 함수 호출
fetch_analytics_data = decorator(fetch_analytics_data)  # 가운데 함수 호출
# 이후: fetch_analytics_data() → wrapper() 실행   # 안쪽 함수 호출
```

#### Step 4: 데코레이터 쌓기 (스태킹)

```python
@timer                           # ← 2번째 적용 (바깥)
@retry(max_attempts=3)           # ← 1번째 적용 (안쪽)
def fetch_data(url: str) -> dict:
    ...

# 실행 순서:
# 1. timer의 wrapper가 호출됨 (시간 측정 시작)
# 2. → retry의 wrapper가 호출됨 (재시도 로직)
# 3.   → 원본 fetch_data가 호출됨
# 4. → retry의 wrapper가 결과/예외 처리
# 5. timer의 wrapper가 시간 측정 종료

# 풀어 쓰면:
# fetch_data = timer(retry(max_attempts=3)(fetch_data))
# → 안쪽(retry)부터 적용, 바깥(timer)이 나중에 감쌈
```

> 💡 **데코레이터 스태킹 순서**: 아래에서 위로 적용됨.
> 실행은 위에서 아래로 진입 → 원본 함수 → 아래에서 위로 빠져나옴 (양파 껍질 구조)

> **데코레이터의 장점?**
> 데코레이터의 목적은 **"지금 당장 실행하는 것"**이 아니라,
> **"나중에 이 함수가 호출될 때 추가 기능을 함께 실행하도록 예약하는 것"**

---

```python

```
