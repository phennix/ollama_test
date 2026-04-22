import os
import time
import json
import yaml
import requests
from litellm import Router, completion

# Configuration
OLLAMA_BASE_URL = "http://localhost:11434"
CONFIG_FILE = "litellm_config.yaml"
REPORT_FILE = "ollama_models_report.md"

# Standard Test Suite
TEST_SUITE = {
    "Tool_Management": {
        "prompt": "Extract the name and age from this text: 'John Doe is 28 years old'. Format the response as strict JSON: {\"name\": \"...\", \"age\": ...}. Output ONLY valid JSON, no markdown.",
        "eval_logic": "json_check"
    },
    "Coding": {
        "prompt": "Write a Python function to calculate the Fibonacci sequence. Do not include explanations, output only the python code.",
        "eval_logic": "presence_check"
    },
    "Research": {
        "prompt": "Explain the concept of quantum entanglement in exactly two short sentences.",
        "eval_logic": "length_check"
    },
    "Orchestration": {
        "prompt": "You are an orchestrator agent. Break down the task 'Write a blog post' into exactly 3 high-level actionable steps. Number them 1, 2, and 3.",
        "eval_logic": "list_check"
    }
}


class OllamaEvaluationAgent:
    def __init__(self, config_path):
        # Load LiteLLM Router from YAML config to act as the Analyzer Agent
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        self.router = Router(model_list=config["model_list"])
        self.evaluator_model = "agent-evaluator"

    def get_ollama_models(self):
        """Connects to Ollama server and retrieves installed models."""
        print(f"[*] Connecting to Ollama server at {OLLAMA_BASE_URL}...")
        try:
            response = requests.get(f"{OLLAMA_BASE_URL}/api/tags")
            response.raise_for_status()
            models = [model['name'] for model in response.json().get('models', [])]
            print(f"[*] Found {len(models)} models: {', '.join(models)}")
            return models
        except Exception as e:
            print(f"[!] Failed to fetch models from Ollama: {e}")
            return []

    def run_tests(self, model_name):
        """Runs the standard test suite against a specific model."""
        print(f"\n[*] Testing model: {model_name}...")
        results = {}

        for test_name, test_data in TEST_SUITE.items():
            start_time = time.time()
            try:
                # Call Ollama model via LiteLLM
                response = completion(
                    model=f"ollama/{model_name}",
                    messages=[{"role": "user", "content": test_data["prompt"]}],
                    api_base=OLLAMA_BASE_URL,
                    max_tokens=250,
                    temperature=0.1
                )
                output = response.choices[0].message.content.strip()
                latency = round(time.time() - start_time, 2)

                # Perform basic programmatic validation checks
                passed_constraint = self._validate_test(output, test_data["eval_logic"])

                results[test_name] = {
                    "latency_seconds": latency,
                    "passed_constraint": passed_constraint,
                    "response": output
                }
                print(f"    - {test_name}: {latency}s | Passed Constraints: {passed_constraint}")

            except Exception as e:
                results[test_name] = {"error": str(e)}
                print(f"    - {test_name}: FAILED ({e})")

        return results

    def _validate_test(self, output, logic):
        """Simple programmatic checks to see if the model followed strict formatting instructions."""
        if logic == "json_check":
            try:
                json.loads(output)
                return True
            except:
                return False
        elif logic == "presence_check":
            return "def " in output
        elif logic == "length_check":
            return 1 <= output.count('.') <= 3
        elif logic == "list_check":
            return "1." in output and "2." in output and "3." in output
        return False

    def analyze_results(self, model_name, raw_results):
        """Uses the Agent Evaluator (configured via Litellm) to analyze performance."""
        print(f"[*] Analyzing results for {model_name} using the Evaluator Agent...")

        prompt = f"""
        You are an AI Performance Analyst. Below are the test results for the LLM '{model_name}'.

        Test Results Data:
        {json.dumps(raw_results, indent=2)}

        Please provide a short markdown evaluation for this model addressing:
        1. **Performance Evaluation**: Speed, accuracy, and constraint adherence.
        2. **Recommended Purpose**: What is this model specifically good for? (e.g., Orchestration, Tool Management/JSON, Research/Knowledge, Code Generation).
        3. **Summary**: A one-sentence final verdict.

        Do not use high-level headings like '# Report', just output the analysis sections.
        """

        try:
            response = self.router.completion(
                model=self.evaluator_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Failed to generate analysis: {e}"

    def generate_report(self, all_analyses):
        """Compiles the final markdown report."""
        print(f"\n[*] Generating final report: {REPORT_FILE}")
        with open(REPORT_FILE, "w", encoding="utf-8") as f:
            f.write("# 🤖 Ollama Models Capability Report\n\n")
            f.write("Generated autonomously by the LLM Evaluation Agent.\n\n")
            for model_name, analysis in all_analyses.items():
                f.write(f"## Model: `{model_name}`\n")
                f.write(f"{analysis}\n\n")
                f.write("---\n\n")
        print("[*] Done!")


if __name__ == "__main__":
    agent = OllamaEvaluationAgent(CONFIG_FILE)
    available_models = agent.get_ollama_models()

    if not available_models:
        print("[!] No models found. Make sure Ollama is running.")
        exit(1)

    all_analyses = {}
    for model in available_models:
        results = agent.run_tests(model)
        analysis = agent.analyze_results(model, results)
        all_analyses[model] = analysis

    agent.generate_report(all_analyses)