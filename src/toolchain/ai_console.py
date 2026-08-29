import urllib.request
import json
import time
import os
import sys
import tempfile
import subprocess
import re

def get_env_var(name):
    v = os.getenv(name)
    if v: return v
    for candidate in [".env", os.path.expanduser("~/.nyx/.env"), os.path.join(os.path.dirname(__file__), "..", "..", ".env")]:
        if os.path.exists(candidate):
            try:
                with open(candidate, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith(f"{name}="):
                            return line.split("=", 1)[1].strip().strip('"').strip("'")
            except: pass
    return ""

KIMI_KEY = get_env_var("NVIDIA_KIMI_KEY")
NEMOTRON_KEY = get_env_var("NVIDIA_NEMOTRON_KEY")
DEEPSEEK_KEY = get_env_var("DEEPSEEK_API_KEY")
OPENROUTER_KEY = get_env_var("OPENROUTER_API_KEY")

EFFORT_LEVEL = "high"  # Options: 'medium', 'high'
MAX_TOKENS = 1200

def set_effort(level):
    global EFFORT_LEVEL, MAX_TOKENS
    if level.lower() in ("medium", "med"):
        EFFORT_LEVEL = "medium"
        MAX_TOKENS = 800
        print(f"\033[92m[OK] Thinking effort set to: MEDIUM (max_tokens: {MAX_TOKENS})\033[0m")
    elif level.lower() in ("high", "hi"):
        EFFORT_LEVEL = "high"
        MAX_TOKENS = 1500
        print(f"\033[92m[OK] Thinking effort set to: HIGH (max_tokens: {MAX_TOKENS})\033[0m")
    else:
        print("Usage: :effort <medium|high>")

def call_deepseek(prompt, system_prompt="You are the Lead Language Architect for Nyx. Perform deep analysis."):
    url = "https://api.deepseek.com/chat/completions"
    headers = {"Authorization": f"Bearer {DEEPSEEK_KEY}", "Content-Type": "application/json"}
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": f"{system_prompt} (Effort Level: {EFFORT_LEVEL.upper()})"},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": MAX_TOKENS
    }
    t0 = time.time()
    req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers=headers)
    with urllib.request.urlopen(req, timeout=30) as res:
        out = json.loads(res.read().decode("utf-8"))
        return (time.time() - t0, out["choices"][0]["message"]["content"].strip())

def call_auditor(prompt, system_prompt="You are the Principal Systems & Security Auditor for Nyx."):
    t0 = time.time()
    # Try OpenRouter Nemotron 550B with reasoning effort parameter
    try:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {"Authorization": f"Bearer {OPENROUTER_KEY}", "Content-Type": "application/json"}
        data = {
            "model": "nvidia/nemotron-3-ultra-550b-a55b",
            "messages": [
                {"role": "system", "content": f"{system_prompt} Conduct a rigorous, high-effort audit."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": MAX_TOKENS,
            "reasoning": {"effort": EFFORT_LEVEL}
        }
        req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers=headers)
        with urllib.request.urlopen(req, timeout=45) as res:
            out = json.loads(res.read().decode("utf-8"))
            ans = out["choices"][0]["message"]["content"].strip()
            return ("Nemotron 3 Ultra 550B (High Reasoning)", time.time() - t0, ans)
    except Exception:
        pass

    # Fallback to DeepSeek
    t, ans = call_deepseek(prompt, system_prompt)
    return ("DeepSeek Auditor (Failover)", t, ans)

def call_synthesizer(prompt, system_prompt="You are the Consensus Synthesizer and Polyglot Hardener for Nyx."):
    t0 = time.time()
    if KIMI_KEY:
        try:
            url = "https://integrate.api.nvidia.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {KIMI_KEY}", "Content-Type": "application/json"}
            data = {
                "model": "moonshotai/kimi-k3",
                "messages": [
                    {"role": "system", "content": f"{system_prompt} Synthesize flawless production code."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": MAX_TOKENS
            }
            req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers=headers)
            with urllib.request.urlopen(req, timeout=25) as res:
                out = json.loads(res.read().decode("utf-8"))
                msg = out["choices"][0]["message"]
                ans = (msg.get("content") or msg.get("reasoning_content") or "").strip()
                if ans:
                    return ("Kimi K3", time.time() - t0, ans)
        except Exception:
            pass

    t, ans = call_deepseek(prompt, system_prompt)
    return ("DeepSeek Synthesizer (Failover)", t, ans)

def run_team_pipeline(task):
    print("\n\033[96m===================================================================")
    print(f"[*] 🚀 DEEP REASONING AI TEAM PIPELINE (Effort: \033[92m{EFFORT_LEVEL.upper()}\033[96m)")
    print(f"    Task: {task}")
    print("===================================================================\033[0m\n")

    # Step 1: Deep Architect
    print(f"\033[90m[*] Step 1: Lead Architect (DeepSeek Platform) conducting deep analysis & initial design...\033[0m")
    p1 = f"""User Task: {task}
Your Mission:
1. Conduct a deep architectural review of how this should be designed in Nyx to ensure it is the easiest, cleanest, and most ergonomic implementation.
2. Provide the complete, idiomatic Nyx code implementation with strong types, guard statements, and methods."""
    t1, res1 = call_deepseek(p1)
    print(f"\033[92m[1. ARCHITECT: DeepSeek Platform ({t1:.2f}s)]\033[0m")
    print(res1)
    print()

    # Step 2: Deep Auditor
    print(f"\033[90m[*] Step 2: Systems Auditor (Nemotron 3 Ultra 550B) performing high-scrutiny code audit...\033[0m")
    p2 = f"""Task: {task}
The Lead Architect proposed this architecture and code:
---
{res1}
---
Perform a thorough, high-effort systems audit:
1. Identify all edge cases, potential memory leaks, buffer overruns, or contract violations (e.g. invalid arguments, negative bounds).
2. Evaluate branch predictability and compiler optimization (CMOV/branchless, loop unrolling, cache locality).
3. Formulate the hardened, production-grade refactor with defensive asserts/guards."""
    name2, t2, res2 = call_auditor(p2)
    print(f"\033[93m[2. AUDITOR: {name2} ({t2:.2f}s) reviewing Step 1]\033[0m")
    print(res2)
    print()

    # Step 3: Consensus Synthesizer
    print(f"\033[90m[*] Step 3: Consensus Synthesizer harmonizing design and audit into finalized flawless code...\033[0m")
    p3 = f"""Task: {task}
Architect Proposal:
---
{res1}
---
Auditor Critique & Hardening:
---
{res2}
---
Your Mission:
Harmonize the architect's elegance with the auditor's strict performance and safety guarantees.
Produce the definitive, 100% complete Nyx code inside ```nyx ... ```."""
    name3, t3, res3 = call_synthesizer(p3)
    print(f"\033[95m[3. CONSENSUS SYNTHESIZER: {name3} ({t3:.2f}s)]\033[0m")
    print(res3)
    print()

    # Extract Nyx code block and run local compilation test
    match = re.search(r"```nyx\s*(.*?)\s*```", res3, re.DOTALL)
    if not match:
        match = re.search(r"```\s*(.*?)\s*```", res3, re.DOTALL)
    
    if match:
        code = match.group(1).strip()
        print("\033[96m===================================================================")
        print("[*] 🛠️ VERIFYING CONSENSUS CODE ON LOCAL NYX COMPILER...")
        print("===================================================================\033[0m")
        with tempfile.NamedTemporaryFile(suffix=".nyx", delete=False, mode="w", encoding="utf-8") as f:
            f.write(code + "\n\nprint(\"[OK] AI Team consensus code verified and executed on local compiler!\");\n")
            temp_path = f.name
        
        try:
            res = subprocess.run(["nyx", "run", temp_path, "--target", "hepy"], capture_output=True, text=True, timeout=10)
            if res.stdout:
                print(res.stdout.strip())
            if res.returncode == 0:
                print("\033[92m✔ [COMPILER PASS]: Zero compilation errors! Production-ready.\033[0m\n")
            else:
                if res.stderr:
                    print(f"\033[91m[Compiler notice]: {res.stderr.strip()}\033[0m")
        except Exception as e:
            print(f"\033[93m[Local Run Notice]: {e}\033[0m")
        finally:
            try: os.remove(temp_path)
            except: pass

def start_console():
    print(f"""
\033[96m===================================================================
⚡ NYX AI COLLABORATIVE TEAM CONSOLE — MULTI-AGENT PIPELINE
===================================================================\033[0m
Your Engineering Team is Assembled:
  • Lead Architect:        DeepSeek Platform
  • Systems Reviewer:      Nemotron 3 Ultra 550B (High Reasoning)
  • Consensus Synthesizer: Kimi K3 / DeepSeek
  • Local Integrator:      Antigravity Engine & Clang/LLVM

Reasoning Effort: \033[92m{EFFORT_LEVEL.upper()}\033[0m
Commands:
  :effort <medium|high>   Toggle reasoning effort
  :exit                   Quit team console
""")

    while True:
        try:
            cmd = input(f"\033[92mnyx-team [{EFFORT_LEVEL}]>\033[0m ").strip()
            if not cmd:
                continue
            if cmd in (":exit", ":quit", "exit", "quit"):
                print("Dismissing Nyx AI Team.")
                break
            if cmd.startswith(":effort"):
                parts = cmd.split()
                if len(parts) > 1:
                    set_effort(parts[1])
                else:
                    print(f"Current effort: {EFFORT_LEVEL}. Usage: :effort <medium|high>")
                continue
            run_team_pipeline(cmd)
        except KeyboardInterrupt:
            print("\nType :exit to quit.")
        except EOFError:
            break

if __name__ == "__main__":
    start_console()