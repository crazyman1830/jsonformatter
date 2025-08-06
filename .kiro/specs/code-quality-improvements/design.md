# Design Document

## Overview

이 설계는 현재 JSON 포맷터 프로젝트의 코드 품질과 구조를 개선하여 더 유지보수하기 쉽고 확장 가능한 아키텍처로 전환하는 것을 목표로 합니다. 주요 개선사항으로는 타입 힌트 추가, 체계적인 로깅 시스템, 환경 변수 관리, 객체지향적 구조 개선, 그리고 정적 분석 도구 통합이 포함됩니다.

## Architecture

### Current Architecture Issues
- 단일 파일에 모든 로직이 집중됨 (app.py, views.py)
- 비즈니스 로직과 웹 프레임워크 코드가 혼재
- 설정 관리가 하드코딩되어 있음
- 로깅 시스템 부재
- 타입 안정성 부족

### Target Architecture
```
src/
├── core/
│   ├── __init__.py
│   ├── config.py          # 설정 관리
│   ├── logging.py         # 로깅 설정
│   └── exceptions.py      # 커스텀 예외
├── models/
│   ├── __init__.py
│   └── json_data.py       # JSON 데이터 모델
├── services/
│   ├── __init__.py
│   ├── json_processor.py  # JSON 처리 서비스
│   └── comment_service.py # 주석 관리 서비스
├── web/
│   ├── __init__.py
│   ├── app.py            # Flask 애플리케이션 팩토리
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── api.py        # API 라우트
│   │   └── web.py        # 웹 라우트
│   └── middleware/
│       ├── __init__.py
│       └── logging.py    # 요청 로깅 미들웨어
└── utils/
    ├── __init__.py
    └── validators.py     # 유틸리티 함수
```

## Components and Interfaces

### 1. Configuration Management (core/config.py)

```python
from typing import Optional
from dataclasses import dataclass
from enum import Enum

class Environment(Enum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"

@dataclass
class AppConfig:
    environment: Environment
    debug: bool
    secret_key: str
    host: str
    port: int
    log_level: str
    max_content_length: int

    @classmethod
    def from_env(cls) -> 'AppConfig':
        """환경 변수에서 설정을 로드"""
        pass
```

### 2. Logging System (core/logging.py)

```python
import logging
from typing import Optional
from core.config import AppConfig

class LoggerFactory:
    @staticmethod
    def create_logger(name: str, config: AppConfig) -> logging.Logger:
        """설정에 따른 로거 생성"""
        pass

    @staticmethod
    def setup_request_logging() -> None:
        """요청 로깅 설정"""
        pass
```

### 3. JSON Data Model (models/json_data.py)

```python
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

@dataclass
class JSONValidationResult:
    is_valid: bool
    error_message: Optional[str] = None
    line_number: Optional[int] = None

@dataclass
class JSONFormatResult:
    success: bool
    formatted_json: Optional[str] = None
    error_message: Optional[str] = None
    line_count: int = 0

class JSONData:
    def __init__(self, raw_data: str):
        self.raw_data = raw_data
        self._parsed_data: Optional[Any] = None
        self._validation_result: Optional[JSONValidationResult] = None

    def validate(self) -> JSONValidationResult:
        """JSON 유효성 검증"""
        pass

    def parse(self) -> Any:
        """JSON 파싱"""
        pass

    @property
    def is_valid(self) -> bool:
        """유효성 검사 결과 반환"""
        pass
```

### 4. JSON Processing Service (services/json_processor.py)

```python
from typing import Optional
from models.json_data import JSONData, JSONFormatResult
from core.logging import LoggerFactory

class JSONProcessorService:
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or LoggerFactory.create_logger(__name__)

    def format_json(self, raw_json: str, indent: int = 2) -> JSONFormatResult:
        """JSON 포맷팅 처리"""
        pass

    def validate_json(self, raw_json: str) -> JSONValidationResult:
        """JSON 유효성 검증"""
        pass

    def get_json_info(self, raw_json: str) -> Dict[str, Any]:
        """JSON 구조 정보 반환"""
        pass
```

### 5. Comment Management Service (services/comment_service.py)

```python
from typing import List, Optional
from abc import ABC, abstractmethod

class CommentStorage(ABC):
    @abstractmethod
    def save_comments(self, session_id: str, comments: List[str]) -> bool:
        pass

    @abstractmethod
    def load_comments(self, session_id: str) -> List[str]:
        pass

class SessionCommentStorage(CommentStorage):
    """세션 기반 주석 저장소"""
    pass

class CommentService:
    def __init__(self, storage: CommentStorage):
        self.storage = storage

    def save_comments(self, session_id: str, comments_text: str) -> bool:
        """주석 저장"""
        pass

    def load_comments(self, session_id: str) -> str:
        """주석 로드"""
        pass

    def clear_comments(self, session_id: str) -> bool:
        """주석 삭제"""
        pass
```

### 6. Web Layer (web/routes/api.py)

```python
from flask import Blueprint, request, jsonify, session
from services.json_processor import JSONProcessorService
from services.comment_service import CommentService
from core.exceptions import ValidationError

class APIRoutes:
    def __init__(self, json_service: JSONProcessorService, comment_service: CommentService):
        self.json_service = json_service
        self.comment_service = comment_service
        self.blueprint = self._create_blueprint()

    def _create_blueprint(self) -> Blueprint:
        """API 블루프린트 생성"""
        pass

    def format_json(self):
        """JSON 포맷팅 엔드포인트"""
        pass

    def validate_json(self):
        """JSON 검증 엔드포인트"""
        pass
```

## Data Models

### JSON Processing Flow
1. **Input Validation**: 입력 데이터 크기 및 형식 검증
2. **JSON Parsing**: 안전한 JSON 파싱 및 오류 처리
3. **Formatting**: 설정된 들여쓰기로 JSON 포맷팅
4. **Response**: 구조화된 응답 반환

### Comment Management Flow
1. **Session Management**: 사용자 세션 기반 주석 관리
2. **Storage**: 추상화된 저장소 인터페이스
3. **Synchronization**: JSON 라인 수와 주석 동기화

## Error Handling

### Custom Exception Hierarchy
```python
class JSONFormatterError(Exception):
    """기본 예외 클래스"""
    pass

class ValidationError(JSONFormatterError):
    """유효성 검증 오류"""
    pass

class ProcessingError(JSONFormatterError):
    """처리 과정 오류"""
    pass

class ConfigurationError(JSONFormatterError):
    """설정 오류"""
    pass
```

### Error Response Format
```python
@dataclass
class ErrorResponse:
    success: bool = False
    error_code: str
    error_message: str
    details: Optional[Dict[str, Any]] = None
```

## Testing Strategy

### Unit Testing Structure
- **Models**: JSON 데이터 모델 테스트
- **Services**: 비즈니스 로직 테스트
- **Web Layer**: API 엔드포인트 테스트
- **Configuration**: 설정 로딩 테스트

### Integration Testing
- **End-to-End**: 전체 JSON 처리 플로우 테스트
- **API**: REST API 통합 테스트

### Code Quality Tools Integration
- **Type Checking**: mypy를 통한 타입 검증
- **Code Style**: black, flake8을 통한 스타일 검증
- **Security**: bandit을 통한 보안 검증
- **Pre-commit Hooks**: 커밋 전 자동 검증

## Configuration Management

### Environment Variables
```bash
# .env.example
FLASK_ENV=development
FLASK_DEBUG=true
SECRET_KEY=your-secret-key-here
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
LOG_LEVEL=INFO
MAX_CONTENT_LENGTH=1048576  # 1MB
```

### Configuration Loading Priority
1. Environment variables
2. .env file
3. Default values
4. Command line arguments (if applicable)

## Logging Strategy

### Log Levels and Usage
- **DEBUG**: 상세한 디버깅 정보
- **INFO**: 일반적인 애플리케이션 동작
- **WARNING**: 주의가 필요한 상황
- **ERROR**: 오류 발생
- **CRITICAL**: 심각한 시스템 오류

### Log Format
```
[%(asctime)s] %(levelname)s in %(module)s: %(message)s
```

### Request Logging
- 요청 URL, 메서드, IP 주소
- 처리 시간
- 응답 상태 코드
- 오류 발생 시 상세 정보

## Deployment Considerations

### Development Tools Setup
- **pyproject.toml**: 모든 도구 설정 통합
- **Makefile**: 개발 명령어 단순화
- **pre-commit**: 코드 품질 자동 검증

### Production Readiness
- 환경별 설정 분리
- 로그 레벨 조정
- 보안 설정 강화
- 성능 모니터링 준비
