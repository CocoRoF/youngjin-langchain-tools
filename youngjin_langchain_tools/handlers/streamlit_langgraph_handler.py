# youngjin_langchain_tools/handlers/streamlit_langgraph_handler.py
"""
Streamlit handler for LangGraph agents.

This module provides a handler class that simplifies streaming
LangGraph agent responses in Streamlit applications.

Replaces the deprecated StreamlitCallbackHandler for LangGraph-based agents.
"""

from typing import Any, Dict, List, Optional, Union, Generator
from dataclasses import dataclass, field
import logging
import re

# Configure logging
logger = logging.getLogger(__name__)


# ============================================================
# Error Patterns for User-Friendly Messages
# ============================================================
ERROR_PATTERNS = {
    # OpenAI errors
    r"AuthenticationError.*API key": {
        "title": "🔑 API Key 오류",
        "message": "API 키가 설정되지 않았거나 유효하지 않습니다.",
        "solution": [
            "1. `.env` 파일에 `OPENAI_API_KEY=sk-...` 형태로 키를 설정하세요.",
            "2. 또는 코드 상단에 직접 API 키를 입력하세요.",
            "3. API 키는 https://platform.openai.com/api-keys 에서 발급받을 수 있습니다.",
        ],
    },
    r"RateLimitError|rate_limit|429": {
        "title": "⏱️ Rate Limit 초과",
        "message": "API 요청 한도를 초과했습니다.",
        "solution": [
            "1. 잠시 후 다시 시도해주세요.",
            "2. API 사용량을 확인하세요: https://platform.openai.com/usage",
            "3. 필요시 요금제를 업그레이드하세요.",
        ],
    },
    r"InsufficientQuotaError|insufficient_quota|billing": {
        "title": "💳 크레딧 부족",
        "message": "API 크레딧이 부족합니다.",
        "solution": [
            "1. 결제 정보를 확인하세요: https://platform.openai.com/account/billing",
            "2. 크레딧을 충전하세요.",
        ],
    },
    r"InvalidRequestError|invalid_request": {
        "title": "❌ 잘못된 요청",
        "message": "API 요청 형식이 올바르지 않습니다.",
        "solution": [
            "1. 입력 데이터를 확인하세요.",
            "2. 모델명이 올바른지 확인하세요.",
        ],
    },
    # Anthropic errors
    r"anthropic.*authentication|ANTHROPIC_API_KEY": {
        "title": "🔑 Anthropic API Key 오류",
        "message": "Anthropic API 키가 설정되지 않았거나 유효하지 않습니다.",
        "solution": [
            "1. `.env` 파일에 `ANTHROPIC_API_KEY=sk-ant-...` 형태로 키를 설정하세요.",
            "2. API 키는 https://console.anthropic.com/ 에서 발급받을 수 있습니다.",
        ],
    },
    # Google errors
    r"google.*api.*key|GOOGLE_API_KEY": {
        "title": "🔑 Google API Key 오류",
        "message": "Google API 키가 설정되지 않았거나 유효하지 않습니다.",
        "solution": [
            "1. `.env` 파일에 `GOOGLE_API_KEY=...` 형태로 키를 설정하세요.",
            "2. API 키는 https://aistudio.google.com/apikey 에서 발급받을 수 있습니다.",
        ],
    },
    # Network errors
    r"ConnectionError|connection.*refused|network": {
        "title": "🌐 네트워크 오류",
        "message": "API 서버에 연결할 수 없습니다.",
        "solution": [
            "1. 인터넷 연결을 확인하세요.",
            "2. 방화벽/프록시 설정을 확인하세요.",
            "3. API 서버 상태를 확인하세요.",
        ],
    },
    r"TimeoutError|timeout|timed out": {
        "title": "⏰ 시간 초과",
        "message": "API 요청이 시간 초과되었습니다.",
        "solution": [
            "1. 네트워크 연결을 확인하세요.",
            "2. 잠시 후 다시 시도해주세요.",
            "3. 요청 크기를 줄여보세요.",
        ],
    },
    # Model errors
    r"model.*not.*found|does not exist|invalid.*model": {
        "title": "🤖 모델 오류",
        "message": "지정된 모델을 찾을 수 없습니다.",
        "solution": [
            "1. 모델명이 올바른지 확인하세요.",
            "2. 해당 모델에 대한 접근 권한이 있는지 확인하세요.",
            "3. 사용 가능한 모델 목록을 확인하세요.",
        ],
    },
}


def _parse_error(error: Exception) -> Dict[str, Any]:
    """Parse an exception and return user-friendly error information."""
    error_str = str(error)
    error_type = type(error).__name__
    full_error = f"{error_type}: {error_str}"

    # Try to match known error patterns
    for pattern, info in ERROR_PATTERNS.items():
        if re.search(pattern, full_error, re.IGNORECASE):
            return {
                "matched": True,
                "title": info["title"],
                "message": info["message"],
                "solution": info["solution"],
                "original_error": error_str[:500],  # Truncate for display
            }

    # Unknown error - return generic info
    return {
        "matched": False,
        "title": "❗ 오류 발생",
        "message": f"{error_type}",
        "solution": ["에러 메시지를 확인하고 문제를 해결해주세요."],
        "original_error": error_str[:500],
    }


@dataclass
class StreamlitLanggraphHandlerConfig:
    """Configuration for StreamlitLanggraphHandler."""

    expand_new_thoughts: bool = True
    """Whether to expand the status container to show tool calls."""

    max_tool_content_length: int = 2000
    """Maximum length of tool output to display before truncating."""

    show_tool_calls: bool = True
    """Whether to display tool call information."""

    show_tool_results: bool = True
    """Whether to display tool execution results."""

    thinking_label: str = "🤔 Thinking..."
    """Label shown while the agent is processing."""

    complete_label: str = "✅ Complete!"
    """Label shown when processing is complete."""

    tool_call_emoji: str = "🔧"
    """Emoji for tool calls."""

    tool_complete_emoji: str = "✅"
    """Emoji for completed tool executions."""

    cursor: str = "▌"
    """Cursor character shown during streaming."""


class StreamlitLanggraphHandler:
    """
    Handler for streaming LangGraph agent responses in Streamlit.

    This class provides a simple interface to visualize LangGraph agent
    execution in Streamlit, similar to how StreamlitCallbackHandler worked
    for the older LangChain AgentExecutor.

    Features:
    - Real-time streaming of agent responses
    - Tool call visualization with expandable details
    - Tool execution results with collapsible output
    - Status indicator showing agent progress
    - Configurable display options

    Example:
        ```python
        import streamlit as st
        from youngjin_langchain_tools import StreamlitLanggraphHandler

        with st.chat_message("assistant"):
            handler = StreamlitLanggraphHandler(
                container=st.container(),
                expand_new_thoughts=True
            )
            response = handler.invoke(
                agent=my_agent,
                input={"messages": [{"role": "user", "content": prompt}]},
                config={"configurable": {"thread_id": thread_id}}
            )
            # response contains the final text
        ```

    For more control, use stream() method:
        ```python
        handler = StreamlitLanggraphHandler(st.container())
        for event in handler.stream(agent, input, config):
            # event contains streaming data if needed
            pass
        final_response = handler.get_response()
        ```
    """

    def __init__(
        self,
        container: Any,
        *,
        expand_new_thoughts: bool = True,
        max_tool_content_length: int = 2000,
        show_tool_calls: bool = True,
        show_tool_results: bool = True,
        thinking_label: str = "🤔 Thinking...",
        complete_label: str = "✅ Complete!",
        config: Optional[StreamlitLanggraphHandlerConfig] = None,
    ):
        """
        Initialize the StreamlitLanggraphHandler.

        Args:
            container: Streamlit container to render content in.
                       Usually st.container() or similar.
            expand_new_thoughts: Whether to expand status container
                                 to show tool calls. Defaults to True.
            max_tool_content_length: Maximum characters of tool output
                                     to display. Defaults to 2000.
            show_tool_calls: Whether to show tool call info. Defaults to True.
            show_tool_results: Whether to show tool results. Defaults to True.
            thinking_label: Label while processing. Defaults to "🤔 Thinking...".
            complete_label: Label when complete. Defaults to "✅ Complete!".
            config: Optional config object. If provided, overrides other params.
        """
        if config is not None:
            self._config = config
        else:
            self._config = StreamlitLanggraphHandlerConfig(
                expand_new_thoughts=expand_new_thoughts,
                max_tool_content_length=max_tool_content_length,
                show_tool_calls=show_tool_calls,
                show_tool_results=show_tool_results,
                thinking_label=thinking_label,
                complete_label=complete_label,
            )

        self._container = container
        self._final_response: str = ""
        self._status_container: Any = None
        self._response_placeholder: Any = None

    @property
    def config(self) -> StreamlitLanggraphHandlerConfig:
        """Get the handler configuration."""
        return self._config

    def get_response(self) -> str:
        """
        Get the final response text after streaming completes.

        Returns:
            The accumulated response text from the agent.
        """
        return self._final_response

    def invoke(
        self,
        agent: Any,
        input: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Invoke the agent and stream the response with visualization.

        This is the main method for simple usage. It handles all the
        streaming complexity and returns the final response.

        Args:
            agent: The LangGraph agent (CompiledGraph) to invoke.
            input: Input dictionary, typically {"messages": [...]}.
            config: Optional config dict with "configurable" key for thread_id etc.

        Returns:
            The final response text from the agent.

        Example:
            ```python
            response = handler.invoke(
                agent=my_agent,
                input={"messages": [{"role": "user", "content": "Hello"}]},
                config={"configurable": {"thread_id": "123"}}
            )
            st.write(response)
            ```
        """
        # Consume the generator to completion
        for _ in self.stream(agent, input, config):
            pass
        return self._final_response

    def stream(
        self,
        agent: Any,
        input: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None,
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Stream agent execution with visualization.

        This method provides more control than invoke(), yielding
        each streaming event for custom processing.

        Args:
            agent: The LangGraph agent (CompiledGraph) to invoke.
            input: Input dictionary, typically {"messages": [...]}.
            config: Optional config dict.

        Yields:
            Dictionary with event information:
            - "type": "tool_call" | "tool_result" | "token" | "complete"
            - "data": Event-specific data

        Example:
            ```python
            for event in handler.stream(agent, input, config):
                if event["type"] == "token":
                    # Custom token handling
                    pass
            ```
        """
        # Import streamlit here to avoid import errors when not using streamlit
        try:
            import streamlit as st
        except ImportError:
            raise ImportError(
                "streamlit is required for StreamlitLanggraphHandler. "
                "Install it with: pip install streamlit"
            )

        # Reset state
        self._final_response = ""

        # Create UI components
        with self._container:
            self._status_container = st.status(
                self._config.thinking_label,
                expanded=self._config.expand_new_thoughts
            )
            self._response_placeholder = st.empty()

        # Stream from agent with error handling
        config = config or {}

        try:
            for stream_mode, data in agent.stream(
                input,
                config=config,
                stream_mode=["messages", "updates"]
            ):
                if stream_mode == "updates":
                    yield from self._handle_updates(data)
                elif stream_mode == "messages":
                    yield from self._handle_messages(data)

            # Mark as complete
            self._status_container.update(
                label=self._config.complete_label,
                state="complete",
                expanded=False
            )

        except Exception as e:
            # Parse error and display user-friendly message
            error_info = _parse_error(e)

            # Update status to show error
            self._status_container.update(
                label="❌ 오류 발생",
                state="error",
                expanded=True
            )

            # Display error in status container
            with self._status_container:
                st.error(f"**{error_info['title']}**")
                st.markdown(f"_{error_info['message']}_")

                st.markdown("**해결 방법:**")
                for solution in error_info["solution"]:
                    st.markdown(f"  {solution}")

                with st.expander("🔍 상세 에러 메시지", expanded=False):
                    st.code(error_info["original_error"], language="text")

            # Log the full error for debugging
            logger.error(f"Agent execution error: {e}", exc_info=True)

            # Yield error event
            yield {
                "type": "error",
                "data": {
                    "error_type": type(e).__name__,
                    "error_info": error_info,
                    "original_error": str(e),
                }
            }
            return  # Stop further processing

        # Final render without cursor
        if self._final_response:
            self._response_placeholder.markdown(self._final_response)

        yield {"type": "complete", "data": {"response": self._final_response}}

    def _handle_updates(
        self,
        data: Dict[str, Any]
    ) -> Generator[Dict[str, Any], None, None]:
        """Handle 'updates' stream mode events."""
        try:
            import streamlit as st
        except ImportError:
            return

        for source, update in data.items():
            if not isinstance(update, dict):
                continue

            messages = update.get("messages", [])
            for msg in messages:
                # Handle tool calls
                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                    if self._config.show_tool_calls:
                        for tc in msg.tool_calls:
                            tool_name = tc.get('name', 'tool')
                            tool_args = tc.get('args', {})

                            with self._status_container:
                                st.write(
                                    f"{self._config.tool_call_emoji} "
                                    f"**{tool_name}**: `{tool_args}`"
                                )

                            yield {
                                "type": "tool_call",
                                "data": {"name": tool_name, "args": tool_args}
                            }

                # Handle tool results
                if source == "tools" and hasattr(msg, 'name'):
                    if self._config.show_tool_results:
                        tool_name = msg.name
                        tool_content = str(msg.content) if hasattr(msg, 'content') else ""

                        with self._status_container:
                            st.write(
                                f"{self._config.tool_complete_emoji} "
                                f"**{tool_name}** 완료"
                            )
                            with st.expander(f"📋 {tool_name} 결과 보기", expanded=False):
                                if len(tool_content) > self._config.max_tool_content_length:
                                    st.code(
                                        tool_content[:self._config.max_tool_content_length]
                                        + "\n... (truncated)",
                                        language="text"
                                    )
                                else:
                                    st.code(tool_content, language="text")

                        yield {
                            "type": "tool_result",
                            "data": {"name": tool_name, "content": tool_content}
                        }

    def _handle_messages(
        self,
        data: tuple
    ) -> Generator[Dict[str, Any], None, None]:
        """Handle 'messages' stream mode events."""
        chunk, metadata = data

        # Skip tool node messages
        if metadata.get("langgraph_node") == "tools":
            return

        # Handle content chunks
        if hasattr(chunk, 'content') and chunk.content:
            # Skip tool call chunks
            if hasattr(chunk, 'tool_call_chunks') and chunk.tool_call_chunks:
                return

            self._final_response += chunk.content
            self._response_placeholder.markdown(
                self._final_response + self._config.cursor
            )

            yield {
                "type": "token",
                "data": {"content": chunk.content, "accumulated": self._final_response}
            }
