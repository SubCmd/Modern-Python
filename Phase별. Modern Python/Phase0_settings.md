# Phase 0: 환경 & 도구 셋업

> **목표**: "그냥 pip install 하고 .py 파일 만들어서 실행"하는 단계에서 →
> **"프로젝트마다 독립된 환경, 자동 포맷팅, 타입 체크가 돌아가는 프로 셋업"**으로 전환
> **ROI**: ⭐ S등급 — 모든 Phase의 토대. 한 번 세팅하면 이후 모든 프로젝트에 적용

---

## 1. 핵심 개념 정리

### 1-1. 왜 환경 셋업이 중요한가?

실무에서 가장 흔한 사고 시나리오:

````
"내 컴퓨터에서는 되는데요?" (It works on my machine)
````

이 문제의 근본 원인은 딱 세 가지:

| 원인 | 설명 | 해결 도구 |
| ---- | ---- | -------- |
| **Python 버전 불일치** | A 프로젝트는 3.10, B 프로젝트는 3.12 필요 | `pyenv` |
| **패키지 버전 충돌** | A 프로젝트의 pandas 1.5가 B 프로젝트의 pandas 2.1과 공존 불가 | `uv` (가상환경 + 패키지 관리) |
| **코드 스타일 불일치** | 팀원마다 들여쓰기, 따옴표, import 순서가 다름 | `ruff` + `pre-commit` |

### 1-2. 도구 한 눈에 보기

````
┌─────────────────────────────────────────────────┐
│                  개발 환경 스택                    │
├─────────────────────────────────────────────────┤
│                                                 │
│  [pyenv]  Python 버전 관리자                      │
│     │     → 여러 Python 버전을 설치하고 전환       │
│     │                                            │
│     ▼                                            │
│  [uv]  패키지 & 프로젝트 관리자                    │
│     │   → 가상환경 생성 + 패키지 설치 (초고속)      │
│     │   → pip + venv + poetry를 하나로 통합        │
│     │                                            │
│     ▼                                            │
│  [pyproject.toml]  프로젝트 설정 파일              │
│     │   → 프로젝트 메타데이터, 의존성, 도구 설정    │
│     │     모두 이 파일 하나에 집중                  │
│     │                                            │
│     ▼                                            │
│  [ruff]  린터 + 포매터 통합                       │
│     │   → 코드 스타일 검사 + 자동 수정             │
│     │   → flake8 + isort + black을 하나로 대체     │
│     │                                            │
│     ▼                                            │
│  [pre-commit]  커밋 전 자동 검사                   │
│        → git commit 할 때 ruff, mypy 자동 실행    │
│                                                  │
└─────────────────────────────────────────────────┘
````

### 1-3. 용어 풀이

| 용어 | 쉬운 설명 |
| ---- | -------- |
| **가상환경 (virtual environment)** | 프로젝트마다 독립된 패키지 보관함. A 프로젝트의 pandas와 B 프로젝트의 pandas가 서로 안 섞임 |
| **린터 (linter)** | 코드를 실행하지 않고 "이 부분 문제 있어요"라고 경고해주는 도구. 맞춤법 검사기와 비슷 |
| **포매터 (formatter)** | 코드의 들여쓰기, 줄바꿈, 따옴표 스타일을 자동으로 통일해주는 도구 |
| **pyproject.toml** | Python 프로젝트의 "신분증". 프로젝트 이름, 버전, 필요한 패키지, 도구 설정을 한 파일에 기록 |
| **lock file** | "지금 이 순간 설치된 패키지의 정확한 버전 목록" 스냅샷. 팀원 모두 동일한 환경 재현 가능 |
| **pre-commit hook** | git commit을 할 때 자동으로 실행되는 검사 슽크립트. 불량 코드가 저장소에 들어가는 걸 막는 문지기 |

---

## 2. Good vs. Bad 예시

### 2-1. Python 버전 관리

````bash
# ❌ Bad: 시스템 Python을 그대로 사용
$ python3 --version
Python 3.8.10  # Ubuntu 기본 → 너무 오래됨. match-case(3.10+) 사용 불가

$ sudo apt install python3.12  # 시스템 Python과 충돌 위험
````

````bash
# ✅ Good: pyenv로 버전 격리
$ pyenv install 3.12.4
$ pyenv local 3.12.4      # 현재 폴더에서만 3.12.4 사용
$ python --version
Python 3.12.4

# 다른 프로젝트 폴더로 이동하면 자동으로 해당 프로젝트의 Python 버전으로 전환
$ cd ~/projects/legacy-app
$ python --version
Python 3.10.14            # .python-version 파일에 기록된 버전으로 자동 전환
````

> 💡 **왜 Good이 나은가**
> pyenv는 프로젝트 폴더에 `.python-version` 파일을 만들어서,
> 폴더에 들어가기만 하면 자동으로 해당 Python 버전이 활성화됨.
> 시스템 Python을 건드리지 않으므로 OS 패키지 관리자와 충돌 없음.


### pyenv 사용법

| 명령어 | 설명 |
| ------ | ---- |
| `pyenv versions` | 설치된 버전 목록 + 현재 선택 표시 |
| `pyenv global 3.12.4` | 전역 기본 설정 |
| `pyenv local 3.12.4` | 현재 폴더만 해당 버전 (`.python-version`생성) |
| `pyenv which python` | 실제 사용 중인 python 경로 확인 |

---

### 2-2. 패키지 관리 & 가상환경

````bash
# ❌ Bad: 전역 pip install
$ pip install fastapi uvicorn langchain pandas
# → 모든 프로젝트가 같은 패키지 공간을 공유
# → A 프로젝트에서 pandas 업그레이드하면 B 프로젝트가 깨질 수 있음

# ❌ Bad: requirements.txt 수동 관리
$ pip freeze > requirements.txt
# → 불필요한 패키지까지 전부 포함 (의존성의 의존성까지)
# → 직접 설치한 패키지와 자동 설치된 패키지 구분 불가
````

````bash
# ✅ Good: uv로 프로젝트 초기화
$ uv init my-project
$ cd my-project

# 패키지 추가 (가상환경 자동 생성 + pyproject.toml에 기록)
$ uv add fastapi uvicorn
$ uv add langchain pandas
$ uv add --dev pytest ruff mypy  # 개발용 패키지는 --dev로 분리

# 결과: pyproject.toml에 직접 설치한 것만 깔끔하게 기록됨
# + uv.lock 파일에 정확한 버전이 고정됨 (lock file)
````

> 💡 **왜 Good이 나은가**:
> - `uv`는 Rust로 만들어져서 pip 대비 **10~100배 빠름**
> - `pyproject.toml`에 "내가 직접 설치한 패키지"만 기록 → 의도가 명확
> - `uv.lock`에 모든 의존성의 정확한 버전 기록 → 팀원 환경 100% 재현
> - `--dev` 플래그로 프로덕션 패키지와 개발 도구 분리

---

## 2-3. pyproject.toml vs. 설정 파일 파편화

````bash
# ❌ Bad: 설정 파일이 여기저기 흩어짐
my-project/
├── setup.py            # 패키지 메타데이터
├── setup.cfg           # 또 다른 메타데이터
├── requirements.txt    # 의존성
├── requirements-dev.txt
├── .flake8             # 린터 설정
├── .isort.cfg          # import 정렬 설정
├── mypy.ini            # 타입 체크 설정
├── pytest.ini          # 테스트 설정
└── black.toml          # 포매터 설정
# → 파일 9개. 어디에 뭐가 있는지 찾기 어려움
````

````bash
# ✅ Good: pyproject.toml 하나에 통합
# pyproject.toml

[project]
name = "metric-copilot"
version = "0.1.0"
description = "자연어 → SQL/Analytics 에이전트"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.115.0",
    "langchain>=0.3.0",
    "pandas>=2.2.0",
    "google-cloud-bigquery>=3.25.0",
]

[dependency-groups]
dev = [
    "pytest>=8.0",
    "ruff>=0.8.0",
    "mypy>=1.13",
]

[tool.ruff]
target-version = "py312"
line-length = 88

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]
# E: 기본 에러, F: pyflakes, I: isort(import 정렬)
# UP: pyupgrade(구식 문법 감지), B: bugbear(흔한 버그)
# SIM: simplify(코드 단순화 제안)

[tool.ruff.format]
quote-style = "double"
indent-style = "space"

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --tb=short"

[tool.mypy]
python_version = "3.12"
strict = true
````

> 💡 **왜 Good이 나은가**:
> - 파일 1개에 프로젝트의 모든 설정이 모여 있음 → 온보딩 속도 향상
> - TOML 형식은 JSON보다 읽기 쉽고, YAML보다 파싱이 명확
> - 2024년 기준 Python 생태계의 공식 표준 (PEP 621)

---

### 2-4. 린터 & 포매터

````python
# ❌ Bad: 도구 없이 수동으로 스타일 관리
import os
import sys
from pathlib import Path
from langchain.chat_models import ChatOpenAI
import json
from typing import Optional,Dict, List
from fastapi import FastAPI,HTTPException

def calculate_ltv(revenue:float,churn_rate:float)->float:
    if churn_rate==0:
        return float('inf')
    return revenue/churn_rate

# 문제점:
# 1. import 순서가 뒤죽박죽 (표준 라이브러리 → 서드파티 → 로컬 순서 아님)
# 2. 타입힌트 콜론/화살표 앞뒤 공백 불일치
# 3. 연산자 앞뒤 공백 누락
````

````python
# ✅ Good: ruff format + ruff check --fix 적용 후
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException
from langchain.chat_models import ChatOpenAI


def calculate_ltv(revenue: float, churn_rate: float) -> float:
    if churn_rate == 0:
        return float("inf")
    return revenue / churn_rate

# ruff가 자동으로:
# 1. import를 표준 라이브러리 / 서드파티 / 로컬 순으로 정렬
# 2. 타입힌트, 연산자 앞뒤 공백 통일
# 3. 따옴표 스타일 통일 (double quote)
````

````bash
# ruff 사용법
$ ruff check .             # 문제 찾기 (린팅)
$ ruff check --fix .       # 자동 수정 가능한 것은 바로 고침
$ ruff format .            # 코드 포매팅 (black 대체)
````

> 💡 **왜 Good이 나은가**:
> - ruff 하나로 flake8 + isort + black + pyupgrade를 모두 대체
> - Rust로 만들어져서 black 대비 **30~100배 빠름**
> - Cursor IDE에서 저장할 때 자동 실행되도록 설정 가능

#### ruff 이용 방법

| 목적 | 명령어 |
| ---- | ----- |
| 문제 검사 | `uv run ruff check .` |
| import 정렬 등 자동 수정 | `uv run ruff check --fix .` |
| 공백, 따옴표 포매팅 | `uv run ruff format .` |
| 한 번에 | `uv run ruff check --fix . && uv run ruff format .` |

---

### 2-5. pre-commit: 커밋 전 자동 검사

````bash
# ❌ Bad: "나중에 정리해야지" 하면서 지저분한 코드가 git에 올라감
$ git add .
$ git commit -m "feat: add LTV calculator"
# → ruff 에러, mypy 에러가 있는 상태로 커밋됨
# → 나중에 코드 리뷰에서 지적받거나, CI에서 실패
````

````yaml
# ✅ Good: .pre-commit-config.yaml 설정
# .pre-commit-config.yaml

repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.6
    hooks:
      - id: ruff          # 린팅
        args: [--fix]
      - id: ruff-format   # 포매팅

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace    # 줄 끝 불필요한 공백 제거
      - id: end-of-file-fixer      # 파일 끝에 빈 줄 추가
      - id: check-yaml             # YAML 문법 검사
      - id: check-toml             # TOML 문법 검사
````


````bash
# 설치 후 동작
$ uv add --dev pre-commit
$ pre-commit install

# 이제 git commit 할 때 자동으로 검사 실행
$ git commit -m "feat: add LTV calculator"
ruff.....................................................Passed
ruff-format..............................................Passed
trailing-whitespace......................................Passed
end-of-file-fixer........................................Passed
# → 모든 검사 통과해야 커밋 완료. 불량 코드 유입 원천 차단
````

> 💡 **왜 Good이 나은가**:
> - 커밋 시점에 자동 검사 → "나중에" = "영원히 안 함" 방지
> - 팀 전체가 동일한 코드 스타일 유지 (설정 파일을 git에 포함)
> - CI에서 실패하기 전에 로컬에서 잡아냄 → 피드백 루프 단축

---

## 3. 실전 예제: 프로젝트 처음부터 세팅하기

### 3-1. Metric Copilot 프로젝트 초기화 (전체 흐름)

````bash
# Step 1: Python 버전 설정
$ pyenv install 3.12.4
$ mkdir metric-copilot && cd metric-copilot
$ pyenv local 3.12.4

# Step 2: uv로 프로젝트 초기화
$ uv init
# → pyproject.toml, .python-version, README.md 자동 생성

# Step 3: 패키지 설치
$ uv add fastapi uvicorn langchain google-cloud-bigquery pandas
$ uv add --dev pytest ruff mypy pre-commit httpx
# httpx: FastAPI 테스트용 비동기 HTTP 클라이언트

# Step 4: 프로젝트 구조 생성
$ mkdir -p src/metric_copilot tests
$ touch src/metric_copilot/__init__.py
$ touch src/metric_copilot/main.py
$ touch tests/__init__.py
$ touch tests/test_main.py
````

최종 디렉토리 구조:

````
metric-copilot/
├── .python-version          # pyenv: "3.12.4"
├── .pre-commit-config.yaml  # pre-commit 설정
├── pyproject.toml           # 프로젝트 설정 통합
├── uv.lock                  # 정확한 패키지 버전 고정
├── README.md
├── src/
│   └── metric_copilot/
│       ├── __init__.py
│       └── main.py
└── tests/
    ├── __init__.py
    └── test_main.py
````

### 3-2. pyproject.toml 완성본

````toml
[project]
name = "metric-copilot"
version = "0.1.0"
description = "자연어 쿼리 → GA4/BigQuery 분석 에이전트"
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn>=0.32.0",
    "langchain>=0.3.0",
    "google-cloud-bigquery>=3.25.0",
    "pandas>=2.2.0",
]

[dependency-groups]
dev = [
    "pytest>=8.3",
    "httpx>=0.28.0",
    "ruff>=0.8.0",
    "mypy>=1.13",
    "pre-commit>=4.0",
]

# ──────────────────────────────────────
# 도구 설정: 모두 이 파일에 집중
# ──────────────────────────────────────

[tool.ruff]
target-version = "py312"
line-length = 88
src = ["src"]                    # import 경로 기준 디렉토리

[tool.ruff.lint]
select = [
    "E",    # pycodestyle 에러 (PEP 8 위반)
    "F",    # pyflakes (미사용 import, 정의되지 않은 변수 등)
    "I",    # isort (import 정렬)
    "UP",   # pyupgrade (구식 Python 문법을 최신으로 변환)
    "B",    # flake8-bugbear (흔한 버그 패턴 감지)
    "SIM",  # flake8-simplify (불필요하게 복잡한 코드 감지)
    "N",    # pep8-naming (변수/함수 네이밍 규칙)
]
ignore = [
    "E501",  # 줄 길이 초과는 formatter에게 맡김
]

[tool.ruff.lint.isort]
known-first-party = ["metric_copilot"]
# → import metric_copilot.xxx 를 "내 코드" 영역으로 인식

[tool.ruff.format]
quote-style = "double"           # 쌍따옴표 통일
indent-style = "space"           # 스페이스 들여쓰기 (탭 아님)
docstring-code-format = true     # docstring 안의 코드도 포매팅

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --tb=short"
# -v: 테스트 이름 상세 출력
# --tb=short: 에러 traceback을 짧게

[tool.mypy]
python_version = "3.12"
strict = true                    # 가장 엄격한 타입 체크 모드
warn_return_any = true           # Any 타입 반환 시 경고
warn_unused_configs = true
````

### 3-3. Cursor IDE 연동 설정

````json
// .vscode/settings.json (Cursor도 이 파일을 사용)
{
    // ruff를 기본 포매터 + 린터로 사용
    "[python]": {
        "editor.defaultFormatter": "charliermarsh.ruff",
        "editor.formatOnSave": true,
        "editor.codeActionsOnSave": {
            "source.fixAll.ruff": "explicit",
            "source.organizeImports.ruff": "explicit"
        }
    },

    // mypy 타입 체크 활성화
    "python.analysis.typeCheckingMode": "strict",

    // 가상환경 경로 (uv가 .venv에 생성)
    "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python"
}
````

> 💡 **이렇게 설정하면**: 파일 저장(Ctrl+S)만 하면 자동으로
> import 정렬 → 코드 포매팅 → 린트 에러 수정이 한 번에 실행됨

---
