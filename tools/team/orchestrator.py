import os
import sys
import json
import urllib.request
import urllib.error

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

def load_env():
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ[k.strip()] = v.strip()

load_env()

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")

def call_openrouter(prompt: str, model: str, system_prompt: str) -> str:
    if not OPENROUTER_API_KEY:
        return "[Error: OPENROUTER_API_KEY missing]"
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://github.com/justsomeone-e/nyx",
        "X-Title": "Nyx Multi-Agent Compiler Team",
        "User-Agent": "NyxCompilerTeam/1.0"
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }
    try:
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        if e.code == 402:
            # Fallback to DeepSeek V4 Flash if Pro requires additional credits
            payload["model"] = "deepseek/deepseek-v4-flash"
            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return f"[Auto-Fallback V4-Flash]: " + data["choices"][0]["message"]["content"]
        return f"[OpenRouter Error: {e}]"

# 1. DeepSeek V4 Flash
def call_deepseek_v4_flash(prompt: str, system_prompt: str = "You are DeepSeek V4 Flash, the ultra-fast compiler and codegen specialist for the nyx programming language.") -> str:
    return call_openrouter(prompt, "deepseek/deepseek-v4-flash", system_prompt)

# 2. DeepSeek V4 Pro
def call_deepseek_v4_pro(prompt: str, system_prompt: str = "You are DeepSeek V4 Pro, Lead Architect and Systems Reasoning Specialist for the nyx programming language.") -> str:
    return call_openrouter(prompt, "deepseek/deepseek-v4-pro", system_prompt)

def team_debate(topic: str):
    print("=" * 70)
    print(f"[TEAM DEBATE] Topic: {topic}")
    print("=" * 70)
    
    print("\n[*] 1. DeepSeek V4 Pro (Lead Architect) Reasoning...")
    pro_opinion = call_deepseek_v4_pro(
        f"Topic: {topic}\n\nPlease provide a concise, high-level architectural proposal for nyx language.",
        system_prompt="You are DeepSeek V4 Pro, Lead Architect of nyx programming language. Focus on API ergonomics, polyglot compiler design, and reliability."
    )
    print(f"\n--- [DeepSeek V4 Pro] ---\n{pro_opinion}\n")
    
    print("\n[*] 2. DeepSeek V4 Flash (Compiler Specialist) Implementation Plan...")
    flash_review = call_deepseek_v4_flash(
        f"Topic: {topic}\n\nArchitectural Proposal:\n{pro_opinion}\n\nProvide exact AST node definitions, parser methods, and codegen emission logic for nyx.",
        system_prompt="You are DeepSeek V4 Flash, Compiler Specialist for nyx language. Focus on fast AST grammar, compiler codegen, and exact code changes."
    )
    print(f"\n--- [DeepSeek V4 Flash] ---\n{flash_review}\n")
    print("=" * 70)
    print("[*] 3. Antigravity: Synthesizing consensus -> Implementing directly into nyx codebase.")
    print("=" * 70)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:])
        team_debate(topic)
    else:
        print("Testing DeepSeek V4 Flash & DeepSeek V4 Pro...")
        f_res = call_deepseek_v4_flash("Say 'DeepSeek V4 Flash online for nyx!' in 1 sentence.")
        print(f"[DeepSeek V4 Flash]: {f_res}")
        p_res = call_deepseek_v4_pro("Say 'DeepSeek V4 Pro online for nyx!' in 1 sentence.")
        print(f"[DeepSeek V4 Pro]: {p_res}")