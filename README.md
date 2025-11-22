# Edge Data Agent (lfedgeai/EDA)
**Data-on-prem, Code-on-the-Fly**

**Inputs:** Data, User Intention, User Preference  
**Outputs:** Applications / Services

> **Rule:** The code in this repo should be generated from data and prompts (not including toolings and basic MCP services).  
> Data, user intention, and preference can be dynamic or static.

# Goals
We focus on AI applications on the edge from both technological & business points of view.

We are monitoring and pushing the boundary of models' intelligence based on on-prem data and algorithms for accurate, useful, efficient, and proactive user experiences.

# Background
Rather than requiring users to upload raw data to cloud platforms, there should be a way that end users can define their tasks, keeps everything local, providing a privacy-preserving and efficient way to interact with and analyze data.

EDA converts a user’s own data into a local on-demand applications or agent service by leveraging the latest auto code generation capabilities of LLMs
- Agent code is generated on the fly the first time the user interacts with the database
- No coding knowledge (maybe even no installation needed if possible) is required for users to build and use
- In contrast to centralized AI platforms, users do not need to upload raw data
- The goal is to allow users to interact with, digest, or serve their own data on-demand without prior application development

# Sandbox Data
- `sandbox/data/` stores the data, agent_card, and input for evaluation
- Run `local_evaluation.py` to evaluate agent performance

## About Tooling
(11/2025) Removed the tool folders but developers can use off-the-shelf code generation tools such as cursor, gemini cli, etc.
(03/2025) we are leveraging the **smolagents** and **llamaindex** frameworks for reading/writing files from the local directory. The agent writes retrieval code automatically.About


# Assumptions
1. The accuracy and robustness of LLM code generation improves to human level (SWEBench https://www.swebench.com/)
2. The cost of autonomous coding goes to negligible
3. The accuracy and user experience can be further improved by local/personal knowledge of the data base and the information of user query history

# Branch Strategy
- **Main Branch:** Targets solving problems with prompts only, with minimum coding
- **Working Branch:** Targets practical solutions using current technologies (provides basic RAG code examples, code functions e.g., writing/reading files, etc.)
