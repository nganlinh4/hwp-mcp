# HWP-MCP (한글 Model Context Protocol)

[![GitHub](https://img.shields.io/github/license/jkf87/hwp-mcp)](https://github.com/jkf87/hwp-mcp)

> **This is an improved fork** with FastMCP v2.11.2 compatibility and enhanced error handling. See [Improvements](#improvements) section for details.

HWP-MCP는 한글 워드 프로세서(HWP)를 Claude와 같은 AI 모델이 제어할 수 있도록 해주는 Model Context Protocol(MCP) 서버입니다. 이 프로젝트는 한글 문서를 자동으로 생성, 편집, 조작하는 기능을 AI에게 제공합니다.

## 주요 기능

- 문서 생성 및 관리: 새 문서 생성, 열기, 저장 기능
- 텍스트 편집: 텍스트 삽입, 글꼴 설정, 단락 추가
- 테이블 작업: 테이블 생성, 데이터 채우기, 셀 내용 설정
- 완성된 문서 생성: 템플릿 기반 보고서 및 편지 자동 생성
- 일괄 작업: 여러 작업을 한 번에 실행하는 배치 기능

## 시스템 요구사항

- Windows 운영체제
- 한글(HWP) 프로그램 설치
- Python 3.7 이상
- 필수 Python 패키지 (requirements.txt 참조)

## 설치 방법

1. 저장소 클론:
```bash
git clone https://github.com/nganlinh4/hwp-mcp.git
cd hwp-mcp
```

2. 의존성 설치:
```bash
pip install -r requirements.txt
```

3. (선택사항) MCP 패키지 설치:
```bash
pip install mcp
```

## 사용 방법

### Claude와 함께 사용하기

Claude 데스크톱 설정 파일에 다음과 같이 HWP-MCP 서버를 등록하세요:

```json
{
  "mcpServers": {
    "hwp": {
      "command": "python",
      "args": ["경로/hwp-mcp/hwp_mcp_stdio_server.py"]
    }
  }
}
```

### 주요 기능 예시

#### 새 문서 생성
```python
hwp_create()
```

#### 텍스트 삽입
```python
hwp_insert_text("원하는 텍스트를 입력하세요.")
```

#### 테이블 생성 및 데이터 입력
```python
# 테이블 생성
hwp_insert_table(rows=5, cols=2)

# 테이블에 데이터 채우기
hwp_fill_table_with_data([
    ["월", "판매량"], 
    ["1월", "120"], 
    ["2월", "150"], 
    ["3월", "180"], 
    ["4월", "200"]
], has_header=True)

# 표에 연속된 숫자 채우기
hwp_fill_column_numbers(start=1, end=10, column=1, from_first_cell=True)
```

#### 문서 저장
```python
hwp_save("경로/문서명.hwp")
```

#### 일괄 작업 예시
```python
hwp_batch_operations([
    {"operation": "hwp_create"},
    {"operation": "hwp_insert_text", "params": {"text": "제목"}},
    {"operation": "hwp_set_font", "params": {"size": 20, "bold": True}},
    {"operation": "hwp_save", "params": {"path": "경로/문서명.hwp"}}
])
```

## 프로젝트 구조

```
hwp-mcp/
├── hwp_mcp_stdio_server.py  # 메인 서버 스크립트
├── requirements.txt         # 의존성 패키지 목록
├── hwp-mcp-구조설명.md       # 프로젝트 구조 설명 문서
├── src/
│   ├── tools/
│   │   ├── hwp_controller.py  # 한글 제어 핵심 컨트롤러
│   │   └── hwp_table_tools.py # 테이블 관련 기능 전문 모듈
│   ├── utils/                 # 유틸리티 함수
│   └── __tests__/             # 테스트 모듈
└── security_module/
    └── FilePathCheckerModuleExample.dll  # 보안 모듈
```

## 트러블슈팅

### 보안 모듈 관련 문제
기본적으로 한글 프로그램은 외부에서 파일 접근 시 보안 경고를 표시합니다. 이를 우회하기 위해 `FilePathCheckerModuleExample.dll` 모듈을 사용합니다. 만약 보안 모듈 등록에 실패해도 기능은 작동하지만, 파일 열기/저장 시 보안 대화 상자가 표시될 수 있습니다.

### 한글 연결 실패
한글 프로그램이 실행 중이지 않을 경우 연결에 실패할 수 있습니다. 한글 프로그램이 설치되어 있고 정상 작동하는지 확인하세요.

### 테이블 데이터 입력 문제
테이블에 데이터를 입력할 때 커서 위치가 예상과 다르게 동작하는 경우가 있었으나, 현재 버전에서는 이 문제가 해결되었습니다. 테이블의 모든 셀에 정확하게 데이터가 입력됩니다.

## 변경 로그

### 2025-03-27
- 표 생성 및 데이터 채우기 기능 개선
  - 표 안에 표가 중첩되는 문제 해결
  - 표 생성과 데이터 채우기 기능 분리
  - 표 생성 전 현재 커서 위치 확인 로직 추가
  - 기존 표에 데이터만 채우는 기능 개선
- 프로젝트 관리 개선
  - .gitignore 파일 추가 (임시 파일, 캐시 파일 등 제외)

### 2025-03-25
- 테이블 데이터 입력 기능 개선
  - 첫 번째 셀부터 정확하게 데이터 입력 가능
  - 셀 선택 및 커서 위치 설정 로직 개선
  - 텍스트 입력 시 커서 위치 유지 기능 추가
- 테이블 전용 도구 모듈(`hwp_table_tools.py`) 추가
- `hwp_fill_column_numbers` 함수에 `from_first_cell` 옵션 추가

## 라이선스

이 프로젝트는 MIT 라이선스에 따라 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 기여 방법

1. 이슈 제보 또는 기능 제안: GitHub 이슈를 사용하세요.
2. 코드 기여: 변경사항을 포함한 Pull Request를 제출하세요.

## 관련 프로젝트

- [HWP SDK](https://www.hancom.com/product/sdk): 한글과컴퓨터의 공식 SDK
- [Cursor MCP](https://docs.cursor.com/context/model-context-protocol#configuration-locations)
- [Smithery](https://smithery.ai/server/@jkf87/hwp-mcp)

## Improvements

This fork includes several improvements over the original project:

### 🔧 **FastMCP v2.11.2 Compatibility**
- Updated FastMCP import from `mcp.server.fastmcp` to `fastmcp`
- Fixed FastMCP initialization parameters for latest version compatibility
- Updated installation instructions to use `pip install fastmcp`

### 🛠️ **Enhanced Error Handling**
- Added UTF-8 encoding support for Korean characters in error messages
- Improved error message handling to prevent encoding crashes
- Better cross-platform compatibility

### 📁 **Path Management**
- Fixed hardcoded security module path to use relative paths
- Improved portability across different system configurations
- Dynamic path resolution for security module DLL

### 🌐 **Internationalization**
- Translated Korean error messages and comments to English
- Improved code readability for international developers
- Maintained Korean documentation for local users

### 📋 **Code Quality**
- Added comprehensive `.gitignore` file
- Improved code documentation and comments
- Better project structure and maintainability

## 연락처

Original project: [jkf87/hwp-mcp](https://github.com/jkf87/hwp-mcp)
프로젝트 관련 문의는 GitHub 이슈, [코난쌤](https://www.youtube.com/@conanssam)를 통해 해주세요.
