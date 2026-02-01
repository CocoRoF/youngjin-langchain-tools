# Quick Start Guide

A comprehensive guide to get started with **youngjin-langchain-tools**.

## Table of Contents

1. [Installation](#installation)
2. [Basic Usage](#basic-usage)
3. [Configuration Options](#configuration-options)
4. [Event Handling](#event-handling)
5. [Migration from StreamlitCallbackHandler](#migration-from-streamlitcallbackhandler)

## Installation

```bash
pip install youngjin-langchain-tools[streamlit]
```

Or using uv:

```bash
uv add youngjin-langchain-tools
uv add streamlit
```

---

## Basic Usage

### Simple Example

```python
import streamlit as st
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from youngjin_langchain_tools import StreamlitLanggraphHandler

# Initialize
st.set_page_config(page_title="My Agent", page_icon="🤖")

# Create agent
llm = ChatOpenAI(model="gpt-4")
checkpointer = InMemorySaver()

agent = create_agent(
    model=llm,
    tools=[your_tool_1, your_tool_2],
    checkpointer=checkpointer,
)

# Chat interface
if prompt := st.chat_input("Ask me anything"):
    st.chat_message("user").write(prompt)

    with st.chat_message("assistant"):
        # Create handler - this is where the magic happens!
        handler = StreamlitLanggraphHandler(
            container=st.container(),
            expand_new_thoughts=True
        )

        # Invoke agent with handler
        response = handler.invoke(
            agent=agent,
            input={"messages": [{"role": "user", "content": prompt}]},
            config={"configurable": {"thread_id": "user-session-1"}}
        )

        # response is already displayed, but you can also use it
        print(f"Final response: {response}")
```

### What You Get

When using `StreamlitLanggraphHandler`, you automatically get:

1. **🤔 Thinking Status**: A status indicator showing the agent is processing
2. **🔧 Tool Calls**: Display of which tools are being called with arguments
3. **✅ Tool Results**: Expandable sections showing tool outputs
4. **Streaming Response**: Real-time token-by-token response display
5. **✅ Complete Status**: Status updates when processing is done

---

## Configuration Options

### Using Individual Parameters

```python
handler = StreamlitLanggraphHandler(
    container=st.container(),
    expand_new_thoughts=True,      # Show tool calls expanded
    max_tool_content_length=2000,  # Truncate long tool outputs
    show_tool_calls=True,          # Display tool call info
    show_tool_results=True,        # Display tool results
    thinking_label="🤔 Thinking...",
    complete_label="✅ Complete!",
)
```

### Using Config Object

```python
from youngjin_langchain_tools import (
    StreamlitLanggraphHandler,
    StreamlitLanggraphHandlerConfig
)

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
```

### Configuration Reference

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `expand_new_thoughts` | bool | True | Auto-expand status to show tool activity |
| `max_tool_content_length` | int | 2000 | Max chars before truncating tool output |
| `show_tool_calls` | bool | True | Show when tools are called |
| `show_tool_results` | bool | True | Show tool execution results |
| `thinking_label` | str | "🤔 Thinking..." | Status label during processing |
| `complete_label` | str | "✅ Complete!" | Status label when done |
| `tool_call_emoji` | str | "🔧" | Emoji for tool calls |
| `tool_complete_emoji` | str | "✅" | Emoji for completed tools |
| `cursor` | str | "▌" | Cursor during streaming |

---

## Event Handling

For more control, use the `stream()` method:

```python
handler = StreamlitLanggraphHandler(st.container())

for event in handler.stream(agent, input, config):
    match event["type"]:
        case "tool_call":
            # Tool is being called
            print(f"Calling: {event['data']['name']}")
            print(f"Args: {event['data']['args']}")

        case "tool_result":
            # Tool execution completed
            print(f"Result from: {event['data']['name']}")
            print(f"Content: {event['data']['content'][:100]}...")

        case "token":
            # New token received
            print(f"Token: {event['data']['content']}")
            # Accumulated response so far
            print(f"So far: {event['data']['accumulated'][:50]}...")

        case "complete":
            # All done
            print(f"Final: {event['data']['response']}")

# Or get response after streaming
final_response = handler.get_response()
```

---

## Migration from StreamlitCallbackHandler

### Before (LangChain < 1.0)

```python
from langchain.callbacks import StreamlitCallbackHandler
from langchain.agents import AgentExecutor

# Create agent executor
agent_executor = AgentExecutor(agent=agent, tools=tools)

with st.chat_message("assistant"):
    st_cb = StreamlitCallbackHandler(
        st.container(),
        expand_new_thoughts=True
    )
    response = agent_executor.invoke(
        {"input": prompt},
        config=RunnableConfig({"callbacks": [st_cb]})
    )
    st.write(response["output"])
```

### After (LangGraph 1.0+)

```python
from youngjin_langchain_tools import StreamlitLanggraphHandler
from langchain.agents import create_agent

# Create LangGraph agent
agent = create_agent(model=llm, tools=tools, checkpointer=checkpointer)

with st.chat_message("assistant"):
    handler = StreamlitLanggraphHandler(
        st.container(),
        expand_new_thoughts=True
    )
    response = handler.invoke(
        agent=agent,
        input={"messages": [{"role": "user", "content": prompt}]},
        config={"configurable": {"thread_id": thread_id}}
    )
    # response is already the final text!
```

### Key Differences

| Aspect | StreamlitCallbackHandler | StreamlitLanggraphHandler |
|--------|--------------------------|---------------------------|
| Agent Type | AgentExecutor | LangGraph CompiledGraph |
| Input Format | `{"input": prompt}` | `{"messages": [...]}` |
| Response | `response["output"]` | Direct string |
| Usage | Pass as callback | Wrap the invoke call |
| Config | RunnableConfig | Direct dict |

---

## Troubleshooting

### Common Issues

**ImportError: streamlit is required**
```bash
pip install streamlit
# or
pip install youngjin-langchain-tools[streamlit]
```

**Agent not streaming properly**

Ensure your agent supports streaming. The handler uses:
```python
agent.stream(input, config, stream_mode=["messages", "updates"])
```

**Tool results not showing**

Check that your tools return string content. Complex objects may need serialization.

---

## Next Steps

- Check out the [API Reference](README.md#api-reference)
- See [examples](examples/) for complete applications
- Read about [custom handlers](docs/custom-handlers.md)
