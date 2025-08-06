# 개발자 가이드

JSON 포맷터 프로젝트의 개발자를 위한 상세 가이드입니다.

## 📋 목차

- [프로젝트 개요](#프로젝트-개요)
- [아키텍처](#아키텍처)
- [개발 환경 설정](#개발-환경-설정)
- [코드 구조](#코드-구조)
- [개발 워크플로우](#개발-워크플로우)
- [테스팅](#테스팅)
- [배포](#배포)
- [기여 가이드라인](#기여-가이드라인)

## 프로젝트 개요

### 기술 스택
- **Backend**: Python 3.8+, Flask 3.0+
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **개발 도구**: Black, Flake8, MyPy, Bandit, Pre-commit
- **패키지 관리**: pip, pyproject.toml

### 주요 특징
- 타입 안전성을 위한 완전한 타입 힌트
- 의존성 주입 패턴 적용
- 체계적인 로깅 시스템
- 환경별 설정 관리
- 포괄적인 오류 처리

## 아키텍처

### 레이어드 아키텍처

```
┌─────────────────────────────────────┐
│           Web Layer                 │
│  (Routes, Middleware, Templates)    │
├─────────────────────────────────────┤
│         Service Layer               │
│   (Business Logic, Processing)      │
├─────────────────────────────────────┤
│          Model Layer                │
│     (Data Models, Validation)       │
├─────────────────────────────────────┤
│          Core Layer                 │
│  (Configuration, Logging, Utils)    │
└─────────────────────────────────────┘
```

### 주요 컴포넌트

#### Core Layer (`src/core/`)
- **config.py**: 환경 변수 관리 및 애플리케이션 설정
- **logging.py**: 중앙화된 로깅 시스템
- **exceptions.py**: 커스텀 예외 클래스 정의

#### Model Layer (`src/models/`)
- **json_data.py**: JSON 데이터 모델 및 검증 로직

#### Service Layer (`src/services/`)
- **json_processor.py**: JSON 포맷팅 및 검증 서비스
- **comment_service.py**: 주석 관리 서비스

#### Web Layer (`src/web/`)
- **app.py**: Flask 애플리케이션 팩토리
- **routes/**: API 및 웹 라우트
- **middleware/**: 요청/응답 미들웨어

## 개발 환경 설정

### 1. 초기 설정

```bash
# 저장소 클론
git clone <repository-url>
cd jsonformatter

# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 개발 의존성 설치
pip install -e ".[dev]"
```

### 2. 환경 변수 설정

```bash
# .env 파일 생성
cp .env.example .env

# 개발용 설정 예시
cat > .env << EOF
FLASK_ENV=development
FLASK_DEBUG=true
SECRET_KEY=dev-secret-key-change-in-production
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
LOG_LEVEL=DEBUG
MAX_CONTENT_LENGTH=1048576
EOF
```

### 3. 개발 도구 설정

```bash
# Pre-commit 훅 설치
pre-commit install

# 설정 확인
pre-commit run --all-files
```

## 코드 구조

### 디렉토리 구조 상세

```
src/
├── core/
│   ├── __init__.py
│   ├── config.py          # AppConfig, Environment enum
│   ├── logging.py         # LoggerFactory, 로깅 설정
│   └── exceptions.py      # 커스텀 예외 클래스들
├── models/
│   ├── __init__.py
│   └── json_data.py       # JSONData, ValidationResult, FormatResult
├── services/
│   ├── __init__.py
│   ├── json_processor.py  # JSONProcessorService
│   └── comment_service.py # CommentService, CommentStorage
├── web/
│   ├── __init__.py
│   ├── app.py            # create_app 팩토리 함수
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── api.py        # APIRoutes 클래스
│   │   └── web.py        # WebRoutes 클래스
│   └── middleware/
│       ├── __init__.py
│       └── logging.py    # RequestLoggingMiddleware
└── utils/
    ├── __init__.py
    └── validators.py     # 유틸리티 함수들
```

### 코딩 컨벤션

#### 타입 힌트
모든 함수와 메서드에 타입 힌트를 사용합니다:

```python
from typing import Dict, List, Optional, Tuple, Any

def process_json(data: str, indent: int = 2) -> Tuple[bool, Optional[str]]:
    """JSON 데이터를 처리합니다."""
    pass

class JSONProcessor:
    def __init__(self, logger: Optional[logging.Logger] = None) -> None:
        self.logger = logger or logging.getLogger(__name__)
```

#### 문서화
모든 클래스와 함수에 docstring을 작성합니다:

```python
def format_json(self, raw_json: str, indent: int = 2) -> JSONFormatResult:
    """
    JSON 문자열을 포맷팅합니다.

    Args:
        raw_json: 포맷팅할 JSON 문자열
        indent: 들여쓰기 레벨 (기본값: 2)

    Returns:
        JSONFormatResult: 포맷팅 결과

    Raises:
        ValidationError: JSON이 유효하지 않은 경우
    """
```

#### 오류 처리
구체적인 예외 처리를 사용합니다:

```python
try:
    result = json.loads(data)
except json.JSONDecodeError as e:
    logger.error(f"JSON parsing failed: {e}")
    raise ValidationError(f"Invalid JSON: {e}")
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
    raise ProcessingError("JSON processing failed")
```

## 개발 워크플로우

### 1. 기능 개발

```bash
# 새 브랜치 생성
git checkout -b feature/new-feature

# 개발 진행
# ... 코드 작성 ...

# 코드 품질 검사
python -m black src/
python -m flake8 src/
python -m mypy src/
python -m bandit -r src/
```

### 2. 테스트 실행

```bash
# 통합 테스트
python test_integration.py

# 정적 분석 테스트
python test_static_analysis.py

# 애플리케이션 시작 테스트
python test_startup.py
```

### 3. 커밋 및 푸시

```bash
# 변경사항 스테이징
git add .

# 커밋 (pre-commit 훅 자동 실행)
git commit -m "feat: add new JSON validation feature"

# 푸시
git push origin feature/new-feature
```

### 4. 코드 리뷰

Pull Request 생성 시 다음 사항을 확인합니다:
- [ ] 모든 테스트 통과
- [ ] 코드 품질 도구 통과
- [ ] 타입 힌트 완성
- [ ] 문서화 완료
- [ ] 로깅 적절히 추가

## 테스팅

### 테스트 종류

#### 1. 통합 테스트 (`test_integration.py`)
- 설정 로딩 테스트
- 로깅 시스템 테스트
- Flask 애플리케이션 생성 테스트
- API 엔드포인트 테스트

#### 2. 정적 분석 테스트 (`test_static_analysis.py`)
- Black 포맷팅 검사
- Flake8 린팅 검사
- MyPy 타입 검사
- Bandit 보안 검사
- Pre-commit 훅 테스트

#### 3. 시작 테스트 (`test_startup.py`)
- 애플리케이션 시작 테스트
- 기본 기능 테스트

### 테스트 실행

```bash
# 모든 테스트 실행
python test_integration.py && python test_static_analysis.py && python test_startup.py

# 개별 테스트 실행
python test_integration.py      # 통합 테스트
python test_static_analysis.py  # 정적 분석
python test_startup.py          # 시작 테스트
```

## 배포

### 개발 환경

```bash
# 개발 서버 실행
python app.py

# 또는 환경 변수와 함께
FLASK_ENV=development FLASK_DEBUG=true python app.py
```

### 운영 환경

```bash
# 환경 변수 설정
export FLASK_ENV=production
export FLASK_DEBUG=false
export SECRET_KEY=strong-random-secret-key

# 애플리케이션 실행
python app.py

# 또는 WSGI 서버 사용 (예: Gunicorn)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:application
```

### Docker 배포 (선택사항)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "app.py"]
```

## 기여 가이드라인

### 코드 스타일
- Python PEP 8 준수 (Black으로 자동 포맷팅)
- 타입 힌트 필수
- Docstring 필수 (Google 스타일)
- 변수명은 영어 사용, 주석은 한국어 가능

### 커밋 메시지
Conventional Commits 형식을 따릅니다:

```
feat: 새로운 기능 추가
fix: 버그 수정
docs: 문서 수정
style: 코드 스타일 변경
refactor: 코드 리팩토링
test: 테스트 추가/수정
chore: 빌드 프로세스 또는 도구 변경
```

### Pull Request
1. 기능 브랜치에서 작업
2. 모든 테스트 통과 확인
3. 코드 리뷰 요청
4. 승인 후 메인 브랜치에 병합

### 이슈 리포팅
- 버그 리포트: 재현 단계, 예상 결과, 실제 결과 포함
- 기능 요청: 사용 사례, 예상 동작 설명
- 질문: 명확하고 구체적인 질문

## 추가 리소스

### 유용한 명령어

```bash
# 코드 품질 검사 (모든 도구)
python -m black src/ && python -m flake8 src/ && python -m mypy src/ && python -m bandit -r src/

# 의존성 업데이트
pip list --outdated
pip install --upgrade package-name

# 가상환경 재생성
deactivate
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

### 문제 해결

#### 일반적인 문제
1. **Import 오류**: `PYTHONPATH` 확인 또는 `pip install -e .` 실행
2. **타입 체크 오류**: `mypy src/`로 개별 확인
3. **Pre-commit 실패**: `pre-commit run --all-files`로 수동 실행

#### 성능 최적화
- 로그 레벨 조정 (운영 환경에서는 WARNING 이상)
- JSON 크기 제한 설정
- 세션 데이터 정리

### 참고 문서
- [Flask 공식 문서](https://flask.palletsprojects.com/)
- [Python 타입 힌트 가이드](https://docs.python.org/3/library/typing.html)
- [Black 코드 포맷터](https://black.readthedocs.io/)
- [MyPy 타입 체커](https://mypy.readthedocs.io/)
