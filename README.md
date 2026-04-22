# 🤖 Ollama Agentic Testing Suite

An automated, agent-driven workflow tool that queries a local Ollama server, fetches available language models, and subjects them to a suite of capability tests. A designated "Evaluator Agent" (via `litellm`) analyzes the raw results to identify the strengths, weaknesses, and optimal use-cases for each local model.

## 🌟 Features
- **Auto-Discovery**: Automatically queries the Ollama API to detect downloaded models.
- **Automated Test Suite**: Evaluates models on Tool Management (JSON extraction), Coding, Fact-based Research, and Orchestration.
- **Latency Tracking**: Measures time-to-completion for responses.
- **Agentic Analysis**: Uses LiteLLM Router to employ an intelligent "Judge" model to grade performance and recommend purposes.
- **Report Generation**: Outputs a clean Markdown report (`ollama_models_report.md`) outlining capabilities.

## 🚀 Getting Started

### 1. Prerequisites
Ensure you have Python 3.8+ installed and Ollama running locally.

```bash
pip install litellm requests pyyaml
```

Make sure your Ollama instance is active:

In a separate terminal or background
```
ollama serve
```

### 2. Configuration
The script utilizes litellm to establish the Evaluator Agent. Edit litellm_config.yaml to designate the brain behind the analysis.
If using OpenAI as the evaluator, export your API key:
```bash
export OPENAI_API_KEY="sk-your-api-key"
```

If you wish to use a local strong model (like Llama-3) as the evaluator, alter litellm_config.yaml to point to model: ollama/llama3.

### 3. Run the Agent Workflow
```bash
python agent.py
```

### 4. Workflow Overview
Connect: Agent connects to http://localhost:11434 and reads the list of models.
Execute Tests: Agent prompts each model under strict conditions to evaluate instruction-following and accuracy.
Analyze: Agent sends latency metrics, success checks, and raw model outputs to the Evaluator LLM.
Report: Agent outputs ollama_models_report.md, detailing the tasks each model is best suited for (e.g., Agent Orchestration, Tool Calls, General Chat).

### 📄 License
MIT