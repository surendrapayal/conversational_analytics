# Agent & ReAct Loop

## Overview

The NLQ agent uses the **ReAct (Reasoning + Acting)** pattern implemented with LangGraph. The agent iteratively reasons about the user's question, decides which SQL tools to call, executes them, observes the results, and repeats until it has enough information to generate a final answer.

---

## ReAct Graph Structure

```
                    ┌─────────────────────────────────┐
                    │           AgentState             │
                    │  user_input, messages, role,     │
                    │  tools_invoked, tool_results,    │
                    │  final_response, vega_spec, ...  │
                    └─────────────────────────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────────┐
                    │          [agent node]             │
                    │  1. Load role-specific tools      │
                    │  2. Semantic memory recall        │
                    │  3. Build enriched system prompt  │
                    │  4. LLM.bind_tools(tools).invoke  │
                    └───────────────┬───────────────────┘
                                    │
                    ┌───────────────▼───────────────────┐
                    │       _should_continue()          │
                    │  last message has tool_calls?     │
                    └───────────────┬───────────────────┘
                                    │
              ┌─────────────────────┴──────────────────────┐
              │ YES                                        │ NO
              ▼                                            ▼
┌─────────────────────────┐              ┌────────────────────────────┐
│      [tools node]       │              │  [response_formatter node] │
│  ToolNode.invoke(state) │              │  Extract text + Vega spec  │
│  Executes SQL tools     │              │  from last AIMessage       │
│  Returns ToolMessages   │              └────────────────┬───────────┘
└────────────┬────────────┘                               │
             │                                            ▼
             └──────────────────────────────────────────END
             (loops back to agent node)
```

---

## AgentState

The LangGraph state is a `TypedDict` that flows through all nodes:

| Field | Type | Description |
|---|---|---|
| `user_input` | `str` | Original user question |
| `user_id` | `str \| None` | User identifier |
| `conversation_id` | `str` | UUID for this conversation |
| `messages` | `list` | Full message history (auto-merged by LangGraph) |
| `intermediate_steps` | `list[str]` | Human-readable step descriptions |
| `tool_results` | `list[str]` | Raw tool output strings |
| `final_response` | `str` | Extracted final answer text |
| `vega_spec` | `dict \| None` | Parsed Vega-Lite chart spec |
| `thinking` | `str` | Gemini chain-of-thought reasoning |
| `tools_invoked` | `list[str]` | Names of tools called so far |
| `role` | `str \| None` | User role for RBAC |
| `token_usage` | `dict \| None` | Accumulated token counts |
| `prompt` | `str \| None` | System prompt (captured if LOG_PROMPT=true) |

---

## The Four SQL Tools

The `SQLDatabaseToolkit` provides four tools that the LLM uses in sequence:

### 1. `sql_db_list_tables`
Returns the list of table names the role is allowed to access.
- Used by the LLM to discover what data is available.
- SSE label: `"Identifying available data sources"`

### 2. `sql_db_schema`
Returns the DDL schema and sample rows for specified tables.
- Used by the LLM to understand column names, types, and data shape.
- SSE label: `"Analysing data structure"`

### 3. `sql_db_query_checker`
Validates a SQL query before execution — checks for syntax errors and common mistakes.
- Used by the LLM as a self-correction step.
- SSE label: `"Validating query"`

### 4. `sql_db_query`
Executes a SELECT query and returns the result rows.
- The actual data retrieval step.
- SSE label: `"Retrieving data"`

---

## Typical ReAct Iteration Count

For a standard analytics question, the agent typically completes in **4–6 iterations**:

```
Iteration 1: LLM → call sql_db_list_tables
Iteration 2: LLM → call sql_db_schema (for relevant tables)
Iteration 3: LLM → call sql_db_query_checker (validate SQL)
Iteration 4: LLM → call sql_db_query (execute)
Iteration 5: LLM → generate final response (no tool call)
→ response_formatter extracts text + Vega spec
```

Complex queries (multiple joins, aggregations) may require additional schema lookups or query corrections.

---

## Max Iterations Guard

`AGENT_MAX_ITERATIONS` (default: 10) prevents infinite loops. When the limit is reached:
- The agent is forced to respond without calling any more tools.
- A `HumanMessage` is injected: *"You have used the maximum number of tool calls. Based on what you have found so far, provide your final answer now."*
- A warning is logged.

---

## System Prompt

The system prompt is built dynamically per role and contains:

1. **Identity and scope rules** — the agent must not reveal its model, tools, or implementation. It must only answer restaurant data questions.
2. **Data access rules** — only the role's allowed tables, read-only SELECT queries, always aggregate (never dump full tables).
3. **Visualization rules** — when and how to generate Vega-Lite charts (13 chart types with decision guide).
4. **Semantic layer** — business rules, role context, SQL patterns, join guide, available metrics (injected from `semantic_layer.json`).
5. **Memory context** — semantically similar past conversations (injected at runtime, first turn only).

---

## Vega-Lite Chart Generation

The LLM is instructed to append a Vega-Lite spec as a fenced code block when the result has 2+ rows with at least one numeric column:

````
```vega
{
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "width": 700,
  "height": 400,
  "title": "Top 10 Best-Selling Menu Items",
  "mark": "bar",
  ...
}
```
````

The `response_formatter_node` extracts this block, parses it as JSON, validates it (checks for `mark`, `layer`, `spec`, `hconcat`, `vconcat`, or `concat` keys), and returns it as `vega_spec`. The clean text response has the code block removed.

The system prompt includes a **13-type chart decision guide** to help the LLM choose the right chart type based on data shape and query intent (bar, line, area, scatter, heatmap, pie/donut, histogram, box plot, etc.).

---

## Token Usage Tracking

Token usage is accumulated across all LLM calls within a single conversation:

```python
token_usage = {
    "input_tokens":    <total across all agent iterations>,
    "output_tokens":   <total>,
    "total_tokens":    <total>,
    "reasoning_tokens": <Gemini thinking tokens>,
    "cache_read_tokens": <cached input tokens>,
}
```

This is stored in `query_log.token_usage` (JSONB) for cost analysis.

---

## Gemini Thinking Mode

The LLM is configured with `thinking_level="medium"` and `include_thoughts=True`. This enables Gemini's chain-of-thought reasoning:
- The model produces internal reasoning before its final response.
- Thinking content is extracted from `response.additional_kwargs["thinking"]` and stored in `AgentState.thinking`.
- In verbose SSE mode, thinking is streamed as `event: thinking` events.
- Thinking tokens are tracked separately in `token_usage.reasoning_tokens`.
