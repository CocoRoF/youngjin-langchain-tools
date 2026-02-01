# youngjin-langchain-tools

**youngjin-langchain-tools** is a collection of LangGraph utilities designed to simplify AI application development with Streamlit and other frameworks.

## Features

- **StreamlitLanggraphHandler**: A drop-in replacement for the deprecated `StreamlitCallbackHandler`, designed for LangGraph agents
- **Real-time Streaming**: Stream agent responses with live token updates
- **Tool Visualization**: Display tool calls and results with expandable UI components
- **Configurable**: Customize display options, labels, and behavior

## Installation

```bash
pip install youngjin-langchain-tools
```

Or using uv:

```bash
uv add youngjin-langchain-tools
```

With Streamlit support:

```bash
pip install youngjin-langchain-tools[streamlit]
```

## Quick Start

### Basic Usage with LangGraph Agent

```python
import streamlit as st
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents import create_agent
from youngjin_langchain_tools import StreamlitLanggraphHandler

# Create your LangGraph agent
agent = create_agent(
    model=llm,
    tools=tools,
    checkpointer=InMemorySaver(),
)

# In your Streamlit app
with st.chat_message("assistant"):
    handler = StreamlitLanggraphHandler(
        container=st.container(),
        expand_new_thoughts=True
    )

    response = handler.invoke(
        agent=agent,
        input={"messages": [{"role": "user", "content": prompt}]},
        config={"configurable": {"thread_id": thread_id}}
    )

    # response contains the final text
```

### Before & After Comparison

**Before (LangChain < 1.0 with AgentExecutor):**

```python
from langchain.callbacks import StreamlitCallbackHandler

with st.chat_message("assistant"):
    st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=True)
    response = agent_executor.invoke(
        {"input": prompt},
        config=RunnableConfig({"callbacks": [st_cb]})
    )
    st.write(response["output"])
```

**After (LangGraph with StreamlitLanggraphHandler):**

```python
from youngjin_langchain_tools import StreamlitLanggraphHandler

with st.chat_message("assistant"):
    handler = StreamlitLanggraphHandler(st.container(), expand_new_thoughts=True)
    response = handler.invoke(
        agent=langgraph_agent,
        input={"messages": [{"role": "user", "content": prompt}]},
        config={"configurable": {"thread_id": thread_id}}
    )
    # response is the final text directly
```

### Advanced Usage with Custom Configuration

```python
from youngjin_langchain_tools import (
    StreamlitLanggraphHandler,
    StreamlitLanggraphHandlerConfig
)

# Create custom configuration
config = StreamlitLanggraphHandlerConfig(
    expand_new_thoughts=True,
    max_tool_content_length=3000,
    show_tool_calls=True,
    show_tool_results=True,
    thinking_label="🧠 Processing...",
    complete_label="✨ Done!",
    tool_call_emoji="⚡",
    tool_complete_emoji="✓",
    cursor="█",
)

handler = StreamlitLanggraphHandler(
    container=st.container(),
    config=config
)

# Use stream() for more control
for event in handler.stream(agent, input, config):
    if event["type"] == "tool_call":
        print(f"Tool called: {event['data']['name']}")
    elif event["type"] == "token":
        # Custom token handling
        pass

final_response = handler.get_response()
```

## API Reference

### StreamlitLanggraphHandler

Main handler class for streaming LangGraph agents in Streamlit.

#### Constructor Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `container` | Any | required | Streamlit container to render in |
| `expand_new_thoughts` | bool | `True` | Expand status container for tool calls |
| `max_tool_content_length` | int | `2000` | Max chars of tool output to display |
| `show_tool_calls` | bool | `True` | Show tool call information |
| `show_tool_results` | bool | `True` | Show tool execution results |
| `thinking_label` | str | `"🤔 Thinking..."` | Label while processing |
| `complete_label` | str | `"✅ Complete!"` | Label when complete |
| `config` | Config | `None` | Optional config object |

#### Methods

| Method | Description |
|--------|-------------|
| `invoke(agent, input, config)` | Execute agent and return final response |
| `stream(agent, input, config)` | Generator yielding streaming events |
| `get_response()` | Get accumulated response text |

### StreamlitLanggraphHandlerConfig

Configuration dataclass for handler customization.

## Architecture

```
youngjin_langchain_tools/
├── __init__.py              # Package exports
├── handlers/                # UI framework handlers
│   ├── __init__.py
│   └── streamlit_langgraph_handler.py
└── utils/                   # Utility functions
    ├── __init__.py
    └── config.py
```

## Requirements

- Python 3.12+
- LangGraph 0.2+
- Streamlit 1.30+ (optional, for StreamlitLanggraphHandler)

## License

Apache License 2.0 - see [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
