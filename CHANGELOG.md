# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.1] - 2026-02-01

### Added
- **User-Friendly Error Handling**: 에러 발생 시 친화적인 메시지 표시
  - API Key 오류 (OpenAI, Anthropic, Google) 자동 감지 및 해결 방법 안내
  - Rate Limit, 크레딧 부족, 네트워크 오류 등 다양한 에러 패턴 지원
  - 상세 에러 메시지를 접을 수 있는 expander로 표시
  - `error` 이벤트 타입 추가 - 에러 발생 시 yield

### Changed
- `stream()` 메서드에 try-catch 에러 핸들링 추가
- 에러 발생 시 status container가 "error" 상태로 업데이트

## [0.1.0] - 2026-02-01

### Added
- **StreamlitLanggraphHandler**: Main handler class for LangGraph agents in Streamlit
  - `invoke()` method for simple usage - returns final response directly
  - `stream()` method for advanced usage - yields events for custom handling
  - `get_response()` method to retrieve accumulated response

- **StreamlitLanggraphHandlerConfig**: Configuration dataclass
  - `expand_new_thoughts`: Control status container expansion
  - `max_tool_content_length`: Limit tool output display length
  - `show_tool_calls`: Toggle tool call display
  - `show_tool_results`: Toggle tool result display
  - Customizable labels and emojis

- **Event System**: Stream events for tool calls, results, and tokens
  - `tool_call`: When a tool is invoked
  - `tool_result`: When a tool returns results
  - `token`: When a response token is received
  - `complete`: When processing is finished

- **Documentation**
  - README with Before/After migration examples
  - QUICKSTART guide with detailed usage
  - CONTRIBUTING guidelines
  - Apache 2.0 License

### Features
- Drop-in replacement for deprecated StreamlitCallbackHandler
- Real-time streaming with cursor animation
- Expandable tool result sections
- Truncation of long tool outputs
- Full type hints and docstrings

[Unreleased]: https://github.com/yourusername/youngjin-langchain-tools/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/yourusername/youngjin-langchain-tools/releases/tag/v0.1.0
