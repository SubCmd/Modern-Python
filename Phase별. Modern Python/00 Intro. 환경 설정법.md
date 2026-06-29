# 1. 개념 이해하기
1. pyenv : 3.10 / 3.12 등 인터프리터 자체를 바꿈
2. venv : 같은 Python 버전 안에서 패키지(pandas 등)를 프로젝트별로 격리

---

# 2-1. Windows에 pyenv 설치
## 방법 A: pip로 설치 (간단)
pip install pyenv-win --target $HOME\.pyenv

## 방법 B: Git clone
git clone https://github.com/pyenv-win/pyenv-win.git $HOME\.pyenv

# 2-2. PATH 등록하기

## 프로필 파일 열기 (없으면 생성됨)
notepad $PROFILE

## 아래 내용 추가
$env:PYENV = "$HOME\.pyenv\pyenv-win\"
$env:PYENV_ROOT = "$HOME\.pyenv\pyenv-win\"
$env:PYENV_HOME = "$HOME\.pyenv\pyenv-win\"
$env:Path = "$env:PYENV_ROOT\bin;$env:PYENV_ROOT\shims;$env:Path"

### 완전히 닫았다가 다시 열어서
pyenv --version

---

## 3. `uv` 이용하는 방법

# uv 설치 (한 번만)
pip install uv

# 가상환경 생성
uv venv

# 활성화
.\.venv\Scripts\Activate.ps1

# 패키지 설치
uv pip install requests
# 또는 pyproject.toml 기반이면
uv sync
