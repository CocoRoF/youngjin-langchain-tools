# youngjin-langchain-tools

**youngjin-langchain-tools** is a collection of LangGraph utilities designed to simplify AI application development with Streamlit and other frameworks.

## Features

- **StreamlitLanggraphHandler**: A drop-in replacement for the deprecated `StreamlitCallbackHandler`, designed for LangGraph agents
- **Real-time Streaming**: Stream agent responses with live token updates
- **Tool Visualization**: Display tool calls and results with expandable UI components
- **LangSmith Integration**: Built-in support for LangSmith feedback collection via `run_id` tracking
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

### LangSmith Feedback Integration

The handler automatically tracks `run_id` for LangSmith feedback collection. This enables users to provide feedback on agent responses.

```python
import streamlit as st
from langsmith import Client
from streamlit_feedback import streamlit_feedback
from youngjin_langchain_tools import StreamlitLanggraphHandler

# Create handler with LangSmith integration (enabled by default)
handler = StreamlitLanggraphHandler(
    container=st.container(),
    enable_langsmith=True,  # Default
    langsmith_run_name="customer_support_agent",  # Optional custom name
)

# Invoke the agent
response = handler.invoke(agent, input, config)

# After execution, run_id is available for feedback
if handler.run_id:
    st.session_state["run_id"] = handler.run_id
    print(f"Run ID: {handler.run_id}")

# Use run_id with LangSmith feedback
def add_feedback():
    run_id = st.session_state.get("run_id")
    if not run_id:
        st.info("No run_id available for feedback.")
        return

    feedback = streamlit_feedback(
        feedback_type="thumbs",
        optional_text_label="Leave a comment",
        key=f"feedback_{run_id}",
    )

    if feedback:
        langsmith_client = Client()
        score = 1 if feedback["score"] == "👍" else 0
        langsmith_client.create_feedback(
            run_id,
            f"thumbs {feedback['score']}",
            score=score,
            comment=feedback.get("text"),
        )
        st.success("Feedback submitted!")

add_feedback()
```

To disable LangSmith integration:

```python
handler = StreamlitLanggraphHandler(
    container=st.container(),
    enable_langsmith=False,  # Disable run_id tracking
)
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
| `enable_langsmith` | bool | `True` | Enable LangSmith run_id tracking |
| `langsmith_project` | str | `None` | LangSmith project name |
| `langsmith_run_name` | str | `"streamlit_agent_run"` | Name for the LangSmith run |
| `config` | Config | `None` | Optional config object |

#### Methods

| Method | Description |
|--------|-------------|
| `invoke(agent, input, config)` | Execute agent and return final response |
| `stream(agent, input, config)` | Generator yielding streaming events |
| `get_response()` | Get accumulated response text |

#### Properties

| Property | Type | Description |
|----------|------|-------------|
| `run_id` | `Optional[str]` | LangSmith run ID for feedback collection |
| `config` | `StreamlitLanggraphHandlerConfig` | Handler configuration |

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
- LangSmith (optional, for feedback integration)

## License

Apache License 2.0 - see [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
