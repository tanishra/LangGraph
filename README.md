# LangGraph
**LangGraph** is a powerful framework built on top of **LangChain** that enables building **stateful, controllable, multi-step AI agent workflows** using graph-based execution.  
LangGraph treats your AI system as a **graph of nodes**, where each node performs a task, and edges define how data flows between them.

In short:

- LangChain → helps you work with models and tools  
- **LangGraph → helps you orchestrate complex LLM workflows as graphs**

If LangChain is the toolbox, **LangGraph is the architecture**.

---

# ❓ Why Do We Need LangGraph If LangChain Already Exists?

LangChain is great for building simple chains, but real AI agents require:

- **Memory**  
- **State management**  
- **Conditional routing**  
- **Loops and iterative improvement**  
- **Human-in-the-loop support**  
- **Parallel execution and orchestration**

LangChain cannot handle these requirements efficiently by itself.

LangGraph solves these limitations by providing:

✔ Stateful graph execution  
✔ Dynamic branching  
✔ Event-driven updates  
✔ Fully observable execution  
✔ Reliable multi-step agent workflows  
✔ Reversible, inspectable execution with checkpoints  

**LangGraph is designed for agent systems**, not simple prompt pipelines.

---

# 🔄 LangChain vs LangGraph — Key Differences

| Feature | LangChain | LangGraph |
|--------|-----------|-----------|
| Workflow structure | Linear chains | Graph-based DAG workflows |
| State management | Limited, mostly per-run | **Persistent, multi-turn, shared state** |
| Control flow | Simple | **Complex (loops, branching, routing)** |
| Agent support | Basic | **Full agentic orchestration** |
| Parallel execution | Hard | **Native parallel nodes** |
| Checkpoints & observability | Limited | **Built-in** |
| Large-scale pipelines | Not ideal | **Production-grade orchestration** |

**Conclusion:**  
LangChain = working with models  
LangGraph = building intelligent agents and systems

---

# 🧠 Core Concepts of LangGraph

This repo will cover all the major patterns:

---

## 1️⃣ Prompt Chaining Workflows

A sequence of LLM calls, where the output of one becomes the input of the next.

Example:
- Step 1: Generate outline  
- Step 2: Expand into article  
- Step 3: Generate summary  

LangGraph handles this cleanly through **Sequential Nodes**.

---

## 2️⃣ Routing Workflows

Dynamically choose the next node based on the LLM output.

Examples:
- Sentiment routing  
- Task classification: “search”, “generate”, “translate”  
- Decision-making agents  

LangGraph enables **conditional edges** for dynamic routing.

---

## 3️⃣ Parallel Workflows

Execute multiple nodes **at the same time**.

Useful for:
- Multi-model ensemble  
- Multiple retrieval strategies  
- Generating diverse responses  

LangGraph uses **fan-out / fan-in edges** for parallelization.

---

## 4️⃣ Orchestrator Workflows

A controller (Orchestrator) decides:

- Which tool to call  
- Whether to reflect  
- Whether to retry  
- When to stop  

Foundation for:
- Tool-using agents  
- Autonomous agents  
- Multi-agent systems  

---

## 5️⃣ Evaluator–Optimizer Workflows (Self-Improving Loops)

Pattern:

1. Generator node: Produces output  
2. Evaluator node: Grades output  
3. Optimizer node: Improves output  
4. Loop until "quality threshold" reached  

LangGraph supports loops with **Feedback Edges**.

---

# 🧩 Core Building Blocks of LangGraph

## 🔷 1. Graph

A **Graph** represents your entire workflow.  
It contains nodes, edges, and a shared state.

You define:
```python
graph = StateGraph(StateType)
```

Then you add nodes:
```python
graph.add_node("name", fn)
```

Graphs allow:

- Linear execution
- Branching
- Loops
- Parallel paths
- Agent tool flows

--- 

## 🔷 2. Nodes

A **Node** is a single step in a LangGraph workflow.  
Every node performs some computation and returns updates to the shared **state**.

A node can be any of the following:

- **LLM call** (e.g., GPT, Claude, local LLMs)  
- **Tool call** (search engines, APIs, code execution, database queries)  
- **Orchestrator** (controller deciding next steps)  
- **Router** (dynamic branching based on conditions)  
- **Retriever** (RAG-based retrieval steps)  
- **Custom Python function** (your own logic)

Nodes are the **building blocks** of LangGraph and define what the agent/system *does* at each step.

---

## 🔷 3. Edges

Edges define **how the workflow moves** from one node to another.  
They represent transitions and flow control in your graph.

### Types of Edges in LangGraph

- **Normal edges**  
  Moves the flow directly from **Node A → Node B**

- **Conditional edges**  
  These enable dynamic LLM-driven routing (e.g., classification, decision-making)

- **Streaming edges**  
  Supports partial outputs (token-level or chunk-level streaming)

- **Loop edges**  
  Used in self-improving or iterative workflows (e.g., evaluator → optimizer → generator loops)

Edges make LangGraph powerful by supporting branching, looping, and reactive behavior.

---

## 🧠 State in LangGraph — The Heart of Everything

State is the **most important concept** in LangGraph.

### 💡 What is State?

State is a **shared memory container** that persists across the entire workflow.  
Each node reads from and writes to this state.

Example state:

```python
{
  "messages": [...],
  "context": "...",
  "intermediate_results": ...
}
```
State forms the “memory” of the agent.

## 📌 Why is State Important?

Agents need a shared memory (State) to perform:

- **Multi-step reasoning**  
- **Tool usage and storing tool results**  
- **Conversational memory**  
- **Iterative refinement loops**  
- **Debugging and checkpoint recovery**  
- **Long-running workflows**

Without **State**, complex workflows would break because nodes would not be able to coordinate or share information.

LangGraph converts your workflow into a **state machine**, making multi-step reasoning:

- **Reliable**  
- **Traceable**  
- **Reproducible**

This is the foundation of agentic behavior.

---

## 🔀 Reducers in LangGraph

Reducers define **how new state updates are merged** with existing state values.

### Example: merging chat messages

```python
def reducer(old, new):
    return old + new
```

## 🔍 Why Reducers Are Needed

Reducers are essential in LangGraph because:

- **Multiple nodes may update the same key** in the shared state  
- Updates must be merged in a **consistent and predictable order**  
- The workflow must remain **deterministic** (same input → same output)  
- They **prevent state conflicts** during parallel or multi-step execution  

Even though reducers are small functions, they are **critical** for ensuring stable, predictable, and conflict-free graph behavior.

---

## ⚙️ LangGraph Execution Model

LangGraph uses an **event-driven, reactive execution model** designed for reliability and intelligent orchestration.

### ✔ Reactive graph updates  
Nodes execute **only when** the specific parts of the state they depend on change.

### ✔ Deterministic execution  
The same state and inputs always produce the **same execution path**.

### ✔ Checkpoint-based persistence  
Every step of the graph is saved, allowing:

- **Debugging**  
- **Undo / time-travel**  
- **Crash recovery**  
- **Full observability**

### ✔ Interruptible execution  
A workflow can pause, wait for **human feedback**, and resume seamlessly.

### ✔ Human-in-the-loop support  
Ideal for workflows requiring approvals, validation, or manual corrections.

### ✔ Parallel node execution  
LangGraph efficiently manages concurrency while using reducers to safely merge parallel updates.

### ✔ Durable workflows  
If the process restarts or crashes, execution continues from the **last stable checkpoint**, ensuring reliability.

---

## 🤝 Contributing

Contributions are **highly welcomed**!

Whether you want to:

- Add new LangGraph examples  
- Improve documentation  
- Fix bugs  
- Suggest new workflows or patterns  
- Raise issues  
- Share optimizations  
- Improve explanations or code structure  

Your contributions are valuable and appreciated.

### 💡 How to Contribute

1. **Fork** the repository  
2. **Create a new branch** for your feature or fix  
3. **Commit** your changes  
4. **Open a Pull Request** describing what you added or improved  

### 🐛 Found an Issue?

If you encounter any bug, error, or want to suggest improvements, feel free to open an **Issue**.  
Feedback helps make this project better for everyone.

---