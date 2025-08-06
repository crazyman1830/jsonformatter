# Implementation Plan

- [x] 1. 프로젝트 구조 설정 및 기본 설정 파일 생성





  - 새로운 디렉토리 구조 생성 (src/, core/, models/, services/, web/, utils/)
  - pyproject.toml에 개발 도구 설정 추가 (black, mypy, flake8, bandit)
  - .env.example 파일 생성 및 환경 변수 정의
  - Makefile 생성으로 개발 명령어 단순화
  - _Requirements: 4.1, 4.2, 5.1, 5.4_

- [x] 2. 핵심 설정 및 로깅 시스템 구현




- [x] 2.1 환경 변수 관리 시스템 구현


  - core/config.py에 AppConfig 클래스 및 Environment enum 구현
  - 환경 변수 로딩 로직 구현 (python-dotenv 사용)
  - 필수 환경 변수 검증 로직 추가
  - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [x] 2.2 로깅 시스템 구현


  - core/logging.py에 LoggerFactory 클래스 구현
  - 환경별 로그 레벨 설정 구현
  - 요청 로깅 미들웨어 구현 (web/middleware/logging.py)
  - 로그 포맷 및 핸들러 설정
  - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [x] 2.3 커스텀 예외 클래스 구현


  - core/exceptions.py에 예외 계층 구조 구현
  - JSONFormatterError, ValidationError, ProcessingError, ConfigurationError 클래스 생성
  - 예외별 적절한 HTTP 상태 코드 매핑
  - _Requirements: 2.3, 6.3_

- [x] 3. 데이터 모델 및 비즈니스 로직 구현










- [x] 3.1 JSON 데이터 모델 구현


  - models/json_data.py에 JSONData, JSONValidationResult, JSONFormatResult 클래스 구현
  - JSON 파싱 및 유효성 검증 로직 구현
  - 타입 힌트를 포함한 모든 메서드 구현
  - _Requirements: 1.1, 1.2, 7.1, 7.3_

- [x] 3.2 JSON 처리 서비스 구현


  - services/json_processor.py에 JSONProcessorService 클래스 구현
  - 기존 json_formatter.py의 로직을 객체지향적으로 리팩토링
  - 로깅 통합 및 오류 처리 개선
  - 의존성 주입 패턴 적용
  - _Requirements: 7.1, 7.2, 7.5, 2.2_

- [x] 3.3 주석 관리 서비스 구현


  - services/comment_service.py에 CommentService 및 CommentStorage 인터페이스 구현
  - SessionCommentStorage 구현으로 세션 기반 주석 저장
  - 추상화를 통한 확장 가능한 구조 구현
  - _Requirements: 7.1, 7.4, 7.5_

- [x] 4. 웹 레이어 리팩토링




- [x] 4.1 Flask 애플리케이션 팩토리 패턴 구현


  - web/app.py에 create_app 함수 리팩토링
  - 설정 기반 애플리케이션 초기화
  - 의존성 주입을 통한 서비스 등록
  - 미들웨어 등록 및 설정
  - _Requirements: 7.5, 5.3, 2.1_

- [x] 4.2 API 라우트 클래스 기반으로 리팩토링


  - web/routes/api.py에 APIRoutes 클래스 구현
  - 기존 views.py의 엔드포인트를 클래스 메서드로 변환
  - 서비스 의존성 주입 및 오류 처리 개선
  - 타입 힌트 및 docstring 추가
  - _Requirements: 1.1, 7.1, 7.5, 4.3_

- [x] 4.3 웹 라우트 분리 및 구현


  - web/routes/web.py에 메인 페이지 라우트 구현
  - 템플릿 렌더링 로직 분리
  - 정적 파일 서빙 설정
  - _Requirements: 7.1, 7.3_

- [ ] 5. 유틸리티 및 검증 로직 구현

- [x] 5.1 유틸리티 함수 구현



  - utils/validators.py에 입력 검증 함수들 구현
  - 재사용 가능한 헬퍼 함수들 구현
  - 타입 힌트 및 docstring 추가
  - _Requirements: 1.1, 4.3, 7.4_

- [ ] 6. 정적 분석 도구 통합 및 설정





- [x] 6.1 타입 체킹 설정 및 적용




  - mypy 설정을 pyproject.toml에 추가
  - 모든 Python 파일에 타입 힌트 적용
  - mypy 오류 수정 및 타입 안정성 확보
  - _Requirements: 1.1, 1.2, 1.3, 6.2_

- [x] 6.2 코드 스타일 도구 설정


  - black, flake8 설정을 pyproject.toml에 통합
  - 기존 .flake8 설정을 pyproject.toml로 이전
  - 모든 코드에 black 포맷팅 적용
  - _Requirements: 4.1, 6.1_

- [x] 6.3 보안 검사 도구 설정


  - bandit 설정 추가 및 보안 검사 실행
  - 보안 취약점 수정
  - _Requirements: 6.3_

- [ ] 6.4 pre-commit 훅 설정


  - .pre-commit-config.yaml 파일 생성
  - black, flake8, mypy, bandit을 pre-commit 훅으로 설정
  - 통합 명령어를 Makefile에 추가
  - _Requirements: 4.2, 6.4_

- [ ] 7. 기존 코드 마이그레이션 및 정리
- [ ] 7.1 기존 파일들을 새 구조로 이전
  - 기존 app.py, views.py, json_formatter.py의 로직을 새 구조로 이전
  - 중복 코드 제거 및 리팩토링
  - 모든 함수와 클래스에 적절한 docstring 추가
  - _Requirements: 4.3, 7.1, 7.2_

- [ ] 7.2 의존성 업데이트 및 정리
  - requirements.txt에 새로운 의존성 추가 (python-dotenv, typing-extensions)
  - pyproject.toml의 의존성과 동기화
  - 개발 의존성을 pyproject.toml의 dev 그룹에 추가
  - _Requirements: 5.2, 5.4_

- [ ] 8. 최종 통합 및 검증
- [ ] 8.1 애플리케이션 통합 테스트
  - 새로운 구조로 애플리케이션 실행 테스트
  - 모든 API 엔드포인트 동작 확인
  - 로깅 시스템 동작 확인
  - 환경 변수 로딩 확인
  - _Requirements: 2.1, 3.1, 5.3_

- [ ] 8.2 정적 분석 도구 실행 및 검증
  - mypy, black, flake8, bandit 모든 도구 실행
  - 발견된 문제점 수정
  - pre-commit 훅 동작 확인
  - _Requirements: 1.2, 4.1, 6.1, 6.2, 6.3, 6.4_

- [ ] 8.3 문서 업데이트
  - README.md에 새로운 개발 환경 설정 방법 추가
  - 코드 구조 변경사항 문서화
  - 개발자 가이드 업데이트
  - _Requirements: 4.4, 5.1_
