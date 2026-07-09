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


```python

```



```python

```



```python

```

```python

```
