# youngjin_langchain_tools/handlers/streamlit_langgraph_handler.py
"""
Streamlit handler for LangGraph agents.

This module provides a handler class that simplifies streaming
LangGraph agent responses in Streamlit applications.

Replaces the deprecated StreamlitCallbackHandler for LangGraph-based agents.
"""

from typing import Any, Dict, List, Optional, Union, Generator
from dataclasses import dataclass, field


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

        # Stream from agent
        config = config or {}

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
