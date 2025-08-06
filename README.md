# JSON 포맷터 with 라인별 주석

JSON 데이터를 포맷팅하고 **각 라인에 주석을 추가**할 수 있는 웹 기반 도구입니다.

## ✨ 주요 기능

- **JSON 포맷팅 & 검증**: 원시 JSON을 깔끔하게 정리하고 오류 검사
- **라인별 주석**: JSON의 각 라인에 개별 주석 추가 가능
- **실시간 줄 강조**: 주석 편집 시 해당 JSON 라인 자동 강조
- **동기화된 스크롤**: JSON과 주석이 함께 스크롤
- **주석 자동 저장**: 페이지 새로고침 후에도 주석 유지
- **향상된 복사**: JSON만 복사하거나 주석과 함께 복사
- **타입 안전성**: 모든 코드에 타입 힌트 적용
- **체계적인 로깅**: 요청 추적 및 오류 모니터링
- **환경별 설정**: 개발/테스트/운영 환경 분리

## 🚀 빠른 시작

### 일반 사용자

#### Windows 사용자
1. `start.bat` 파일을 더블클릭
2. 브라우저에서 `http://localhost:5000` 접속

#### 다른 운영체제
```bash
pip install -r requirements.txt
python app.py
```

### 개발자 환경 설정

#### 1. 저장소 클론 및 환경 설정
```bash
git clone <repository-url>
cd jsonformatter

# 가상환경 생성 (권장)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
venv\Scripts\activate     # Windows

# 개발 의존성 설치
pip install -e ".[dev]"
```

#### 2. 환경 변수 설정
```bash
# .env 파일 생성
cp .env.example .env

# 필요에 따라 .env 파일 수정
# FLASK_ENV=development
# FLASK_DEBUG=true
# SECRET_KEY=your-secret-key-here
```

#### 3. 개발 도구 설정
```bash
# Pre-commit 훅 설치
pre-commit install

# 코드 품질 검사 실행
python -m black src/          # 코드 포맷팅
python -m flake8 src/         # 린팅
python -m mypy src/           # 타입 체킹
python -m bandit -r src/      # 보안 검사
```

#### 4. 애플리케이션 실행
```bash
# 개발 모드로 실행
python app.py

# 또는 Makefile 사용 (Linux/Mac)
make dev
```

### 필수 요구사항
- Python 3.8 이상
- pip (Python 패키지 관리자)

## 📖 사용법

### 기본 사용
1. JSON 데이터를 입력 영역에 붙여넣기
2. "Format JSON" 버튼 클릭
3. 포맷된 결과 확인

### 주석 기능
1. JSON 포맷 후 오른쪽 "Comments" 섹션에서 각 라인에 주석 입력
2. 주석 편집기에서 줄을 클릭하면 해당 JSON 라인이 강조됨
3. 주석은 자동 저장되어 페이지 새로고침 후에도 유지

### 복사 옵션
- **Copy JSON**: JSON만 복사
- **Copy with Comments**: JSON과 주석을 함께 복사 (// 형태)
- **Clear Comments**: 모든 주석 삭제

## 🔌 API 사용

### JSON 포맷팅
```bash
curl -X POST http://localhost:5000/api/format \
  -H "Content-Type: application/json" \
  -d '{"json_data": "{\"key\": \"value\"}", "indent": 2, "sort_keys": true}'
```

### JSON 검증
```bash
curl -X POST http://localhost:5000/api/validate \
  -H "Content-Type: application/json" \
  -d '{"json_data": "{\"key\": \"value\"}"}'
```

### 주석 관리
```bash
# 주석 저장
curl -X POST http://localhost:5000/api/comments \
  -H "Content-Type: application/json" \
  -d '{"comments": "첫 번째 줄 주석\n두 번째 줄 주석"}'

# 주석 로드
curl -X GET http://localhost:5000/api/comments

# 주석 삭제
curl -X DELETE http://localhost:5000/api/comments
```

### API 정보
```bash
curl -X GET http://localhost:5000/api/
```

## � 사용 예시시

### 기본 포맷팅
**입력:** `{"name":"John","age":30}`

**출력:**
```json
{
  "name": "John",
  "age": 30
}
```

### 주석과 함께 사용
**주석 입력:**
```
사용자 정보 객체
사용자 이름
나이
객체 끝
```

**"Copy with Comments" 결과:**
```json
{ // 사용자 정보 객체
  "name": "John", // 사용자 이름
  "age": 30 // 나이
} // 객체 끝
```

## ⚙️ 설정

### 환경 변수

애플리케이션은 다음 환경 변수를 지원합니다:

```bash
# Flask 설정
FLASK_ENV=development          # development, testing, production
FLASK_DEBUG=true              # true/false
FLASK_HOST=127.0.0.1          # 바인딩 호스트
FLASK_PORT=5000               # 포트 번호

# 애플리케이션 설정
SECRET_KEY=your-secret-key    # Flask 세션 암호화 키
MAX_CONTENT_LENGTH=1048576    # 최대 요청 크기 (바이트)

# 로깅 설정
LOG_LEVEL=INFO                # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

### 개발 환경별 설정

#### 개발 환경 (.env)
```bash
FLASK_ENV=development
FLASK_DEBUG=true
LOG_LEVEL=DEBUG
```

#### 운영 환경
```bash
FLASK_ENV=production
FLASK_DEBUG=false
LOG_LEVEL=WARNING
SECRET_KEY=strong-random-secret-key
```

## 🏗️ 프로젝트 구조

```
jsonformatter/
├── src/                      # 소스 코드
│   ├── core/                 # 핵심 모듈
│   │   ├── config.py         # 설정 관리
│   │   ├── logging.py        # 로깅 시스템
│   │   └── exceptions.py     # 커스텀 예외
│   ├── models/               # 데이터 모델
│   │   └── json_data.py      # JSON 데이터 모델
│   ├── services/             # 비즈니스 로직
│   │   ├── json_processor.py # JSON 처리 서비스
│   │   └── comment_service.py # 주석 관리 서비스
│   ├── web/                  # 웹 레이어
│   │   ├── app.py            # Flask 애플리케이션 팩토리
│   │   ├── routes/           # 라우트 모듈
│   │   └── middleware/       # 미들웨어
│   └── utils/                # 유틸리티 함수
├── static/                   # 정적 파일 (CSS, JS)
├── templates/                # HTML 템플릿
├── tests/                    # 테스트 파일
├── .env.example              # 환경 변수 예시
├── pyproject.toml            # 프로젝트 설정 및 도구 설정
├── requirements.txt          # 운영 의존성
└── app.py                    # 애플리케이션 진입점
```

## 🧪 개발자 가이드

### 코드 품질 도구

이 프로젝트는 다음 도구들을 사용하여 코드 품질을 관리합니다:

- **Black**: 코드 포맷팅
- **Flake8**: 린팅 및 스타일 검사
- **MyPy**: 정적 타입 검사
- **Bandit**: 보안 취약점 검사
- **Pre-commit**: 커밋 전 자동 검사

### 개발 워크플로우

1. **코드 작성**
   ```bash
   # 기능 개발
   git checkout -b feature/new-feature
   ```

2. **코드 품질 검사**
   ```bash
   # 자동 포맷팅
   python -m black src/

   # 모든 검사 실행
   python -m flake8 src/
   python -m mypy src/
   python -m bandit -r src/
   ```

3. **테스트 실행**
   ```bash
   # 통합 테스트
   python test_integration.py

   # 정적 분석 테스트
   python test_static_analysis.py
   ```

4. **커밋 및 푸시**
   ```bash
   git add .
   git commit -m "feat: add new feature"  # pre-commit 훅 자동 실행
   git push origin feature/new-feature
   ```

### 새로운 기능 추가

1. **모델 추가**: `src/models/`에 데이터 모델 정의
2. **서비스 추가**: `src/services/`에 비즈니스 로직 구현
3. **라우트 추가**: `src/web/routes/`에 API 엔드포인트 추가
4. **테스트 추가**: 해당 기능에 대한 테스트 작성

### 로깅 사용법

```python
from core.logging import LoggerFactory

logger = LoggerFactory.create_logger(__name__)

logger.debug("디버그 정보")
logger.info("일반 정보")
logger.warning("경고 메시지")
logger.error("오류 발생")
logger.critical("심각한 오류")
```

## 🛠️ 문제 해결

### 일반적인 문제

#### 설치 문제
- **Python 버전**: Python 3.8 이상 필요
- **의존성 충돌**: 가상환경 사용 권장
- **Windows 권한**: 관리자 권한으로 실행

#### 실행 문제
- **포트 충돌**: `FLASK_PORT=8080` 환경변수로 포트 변경
- **환경 변수**: `.env` 파일이 올바르게 설정되었는지 확인
- **로그 확인**: 애플리케이션 로그에서 상세 오류 정보 확인

#### 개발 도구 문제
- **Pre-commit 실패**: `pre-commit run --all-files`로 수동 실행
- **타입 체크 오류**: `mypy src/`로 개별 확인
- **포맷팅 문제**: `black src/`로 자동 수정

### 브라우저 호환성
- Chrome 60+ (권장)
- Firefox 55+
- Safari 11+
- Edge 16+

### 성능 최적화
- JSON 크기 제한: 기본 1MB (MAX_CONTENT_LENGTH로 조정)
- 로그 레벨 조정: 운영 환경에서는 WARNING 이상 권장
- 세션 정리: 주기적으로 불필요한 세션 데이터 정리

## 📄 라이선스

MIT 라이선스
