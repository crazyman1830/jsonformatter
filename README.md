# JSON 포맷터 with 라인별 주석

JSON 데이터를 포맷팅하고 **각 라인에 주석을 추가**할 수 있는 웹 기반 도구입니다.

## ✨ 주요 기능

- **JSON 포맷팅 & 검증**: 원시 JSON을 깔끔하게 정리하고 오류 검사
- **라인별 주석**: JSON의 각 라인에 개별 주석 추가 가능
- **실시간 줄 강조**: 주석 편집 시 해당 JSON 라인 자동 강조
- **동기화된 스크롤**: JSON과 주석이 함께 스크롤
- **주석 자동 저장**: 페이지 새로고침 후에도 주석 유지
- **향상된 복사**: JSON만 복사하거나 주석과 함께 복사

## 🚀 빠른 시작

### Windows 사용자
1. `start.bat` 파일을 더블클릭
2. 브라우저에서 `http://localhost:5000` 접속

### 다른 운영체제
```bash
pip install -r requirements.txt
python app.py
```

### 필수 요구사항
- Python 3.8 이상

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
curl -X POST http://localhost:5000/format \
  -H "Content-Type: application/json" \
  -d '{"json_data": "{\"key\": \"value\"}"}'
```

### 주석 저장/로드
```bash
# 저장
curl -X POST http://localhost:5000/comments \
  -H "Content-Type: application/json" \
  -d '{"comments": "첫 번째 줄 주석\n두 번째 줄 주석"}'

# 로드
curl -X GET http://localhost:5000/comments
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

환경 변수로 포트 변경 가능:
```bash
FLASK_PORT=8080 python app.py
```

## 🛠️ 문제 해결

### 일반적인 문제
- **Python 버전**: Python 3.8 이상 필요
- **포트 충돌**: `FLASK_PORT=8080` 환경변수로 포트 변경
- **Windows**: `start-manual.bat` 실행하여 단계별 설치

### 브라우저 호환성
- Chrome 60+ (권장)
- Firefox 55+
- Safari 11+
- Edge 16+

## 📄 라이선스

MIT 라이선스