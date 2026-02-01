# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
