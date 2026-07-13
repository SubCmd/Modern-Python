# Phase 4: 클래스 & 데이터 모델링

> **목표**: "class를 왜 써야 하는지 모르겠고, 그냥 dict으로 충분한데?" →
> "dataclass로 도메인 모델을 짜고, Pydantic으로 외부 입력을 검증하며, FastAPI가 왜 BaseModel을 쓰는지 체감한다"
> **ROI**: ⭐ S등급 — Pydantic v2는 FastAPI의 절반. dataclass는 모든 Python 프로젝트의 구조화 기본 도구
> **선수 조건**: Phase 1 (타입힌트), Phase 3 (데코레이터, `@property`의 기반)

---

## 1. 핵심 개념 정리

### 1-1. "클래스를 언제 써야 하는가?" 의사결정 트리

```
데이터를 구조화해야 한다
│
├─ 데이터만 담으면 되는가? (메서드 거의 없음)
│   ├─ 불변(immutable)? ─────→ NamedTuple 또는 frozen dataclass
│   ├─ 외부 입력 검증 필요? ──→ Pydantic BaseModel ⭐
│   └─ 내부 데이터 구조화? ──→ @dataclass ⭐
│
├─ 데이터 + 행동(메서드)이 묶여야 하는가?
│   └─ Yes ──→ 일반 class 또는 @dataclass + 메서드
│
├─ dict처럼 쓰되 타입만 고정하고 싶은가?
│   └─ Yes ──→ TypedDict (JSON 응답 타입 명시용)
│
└─ 함수만으로 충분한가?
    └─ Yes ──→ 클래스 불필요. 함수로 해결
```

> 💡 **실무 80% 법칙**: 대부분의 경우 `@dataclass`(내부) + `Pydantic BaseModel`(외부 입력)
> 두 가지만 쓰면 충분. 일반 class를 직접 짜야 하는 경우는 생각보다 드묾.


### 1-2. 용어 풀이

| 용어 | 쉬운 설명 |
|------|-----------|
| **클래스 (class)** | 데이터(속성)와 행동(메서드)을 하나로 묶는 설계도 |
| **인스턴스 (instance)** | 클래스로 실제로 만든 객체. `user = User("김윤섭")` → user가 인스턴스 |
| **`@dataclass`** | "데이터를 담는 클래스"를 자동으로 만들어주는 데코레이터. `__init__`, `__repr__`, `__eq__` 자동 생성 |
| **`BaseModel` (Pydantic)** | 외부 입력 데이터를 검증하고 변환하는 클래스. FastAPI의 요청/응답 모델 |
| **`@property`** | 메서드를 속성처럼 접근하게 해주는 데코레이터. `user.full_name`이 실제로는 함수 호출 |
| **`__slots__`** | 인스턴스가 가질 수 있는 속성을 미리 고정. 메모리 절약 + 오타 방지 |
| **프로토콜 (Protocol)** | "이 메서드를 가지고 있으면 OK"라는 구조적 타입. 상속 없이 인터페이스 정의 |
| **불변 객체 (immutable)** | 생성 후 속성을 바꿀 수 없는 객체. `frozen=True` 옵션 |
| **직렬화 (serialization)** | 객체를 JSON, dict 등 전송/저장 가능한 형태로 변환 |
| **검증 (validation)** | 입력 데이터가 규칙에 맞는지 확인. "나이가 음수면 에러" 같은 것

---
