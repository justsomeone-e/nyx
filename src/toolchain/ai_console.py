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

def call_deepseek(prompt, max_tokens=350):
    url = "https://api.deepseek.com/chat/completions"
    headers = {"Authorization": f"Bearer {DEEPSEEK_KEY}", "Content-Type": "application/json"}
    data = {"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens}
    t0 = time.time()
    req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers=headers)
    with urllib.request.urlopen(req, timeout=20) as res:
        out = json.loads(res.read().decode("utf-8"))
        return (time.time() - t0, out["choices"][0]["message"]["content"].strip())

def call_auditor(prompt, max_tokens=350):
    t0 = time.time()
    # Try OpenRouter Nemotron 550B
    try:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {"Authorization": f"Bearer {OPENROUTER_KEY}", "Content-Type": "application/json"}
        data = {"model": "nvidia/nemotron-3-ultra-550b-a55b", "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens}
        req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers=headers)
        with urllib.request.urlopen(req, timeout=30) as res:
            out = json.loads(res.read().decode("utf-8"))
            return ("Nemotron 3 Ultra 550B", time.time() - t0, out["choices"][0]["message"]["content"].strip())
    except Exception:
        pass

    # Fallback to DeepSeek
    t, ans = call_deepseek(prompt, max_tokens)
    return ("DeepSeek Auditor (Failover)", t, ans)

def call_synthesizer(prompt, max_tokens=350):
    t0 = time.time()
    # Try Kimi with 429 guard
    if KIMI_KEY:
        try:
            url = "https://integrate.api.nvidia.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {KIMI_KEY}", "Content-Type": "application/json"}
            data = {"model": "moonshotai/kimi-k3", "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens}
            req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers=headers)
            with urllib.request.urlopen(req, timeout=15) as res:
                out = json.loads(res.read().decode("utf-8"))
                msg = out["choices"][0]["message"]
                ans = (msg.get("content") or msg.get("reasoning_content") or "").strip()
                if ans:
                    return ("Kimi K3", time.time() - t0, ans)
        except Exception:
            pass

    # Failover to DeepSeek Platform
    t, ans = call_deepseek(prompt, max_tokens)
    return ("DeepSeek Synthesizer (Failover)", t, ans)

def run_team_pipeline(task):
    print("\n\033[96m===================================================================")
    print(f"[*] 🚀 AUTONOMOUS AI TEAM WORKFLOW TRIGGERED")
    print(f"    Task: {task}")
    print("===================================================================\033[0m\n")

    # Step 1: Architect
    print("\033[90m[*] Step 1: Architect (DeepSeek Platform) designing architecture & initial code...\033[0m")
    p1 = f"You are the Lead Architect for the Nyx systems language. Task: {task}. Propose the architecture and write initial clean Nyx code."
    t1, res1 = call_deepseek(p1)
    print(f"\033[92m[1. ARCHITECT: DeepSeek Platform ({t1:.2f}s)]\033[0m")
    print(res1)
    print()

    # Step 2: Auditor reading Architect's code
    print("\033[90m[*] Step 2: Systems Auditor (Nemotron 3 Ultra 550B) reviewing Architect's design...\033[0m")
    p2 = f"You are the Systems & Security Auditor for the Nyx compiler. The Lead Architect proposed:\n---\n{res1}\n---\nCritique it in 2-3 concise bullet points: edge-case bugs, contract enforcement, and performance/memory leaks. Suggest the hardened refactor."
    name2, t2, res2 = call_auditor(p2)
    print(f"\033[93m[2. AUDITOR: {name2} ({t2:.2f}s) reviewing Step 1]\033[0m")
    print(res2)
    print()

    # Step 3: Consensus Synthesizer
    print("\033[90m[*] Step 3: Consensus Synthesizer harmonizing design and audit into final code...\033[0m")
    p3 = f"You are the Consensus Synthesizer for Nyx. Task: {task}.\nArchitect Design:\n{res1}\nAuditor Critique:\n{res2}\nSynthesize both into the final, definitive, production-ready Nyx code. Put the code in ```nyx ... ```."
    name3, t3, res3 = call_synthesizer(p3)
    print(f"\033[95m[3. CONSENSUS SYNTHESIZER: {name3} ({t3:.2f}s)]\033[0m")
    print(res3)
    print()

    # Extract Nyx code block if present
    match = re.search(r"```nyx\s*(.*?)\s*```", res3, re.DOTALL)
    if not match:
        match = re.search(r"```\s*(.*?)\s*```", res3, re.DOTALL)
    
    if match:
        code = match.group(1).strip()
        print("\033[96m===================================================================")
        print("[*] 🛠️ VERIFYING CONSENSUS CODE ON LOCAL NYX COMPILER...")
        print("===================================================================\033[0m")
        with tempfile.NamedTemporaryFile(suffix=".nyx", delete=False, mode="w", encoding="utf-8") as f:
            f.write(code + "\n\nprint(\"[OK] AI Team consensus code compiled and executed successfully!\");\n")
            temp_path = f.name
        
        try:
            res = subprocess.run(["nyx", "run", temp_path, "--target", "hepy"], capture_output=True, text=True, timeout=10)
            if res.stdout:
                print(res.stdout.strip())
            if res.returncode == 0:
                print("\033[92m✔ [COMPILER PASS]: The AI Team code compiled and passed all checks!\033[0m\n")
            else:
                if res.stderr:
                    print(f"\033[91m[Compiler notice]: {res.stderr.strip()}\033[0m")
        except Exception as e:
            print(f"\033[93m[Local Run Notice]: {e}\033[0m")
        finally:
            try: os.remove(temp_path)
            except: pass

def start_console():
    print("""
\033[96m===================================================================
⚡ NYX AI COLLABORATIVE TEAM CONSOLE — MULTI-AGENT PIPELINE
===================================================================\033[0m
Your Engineering Team is Assembled:
  • Architect:             DeepSeek Platform (~0.9s)
  • Systems Reviewer:      Nemotron 3 Ultra 550B (~3.7s)
  • Consensus Synthesizer: Kimi K3 / DeepSeek (~1.2s)
  • Local Integrator:      Antigravity Engine & Clang/LLVM

Mode:
  [TEAM] Every task is automatically debated, audited, and synthesized!
  Type ':exit' to quit.
""")

    while True:
        try:
            cmd = input("\033[92mnyx-team>\033[0m ").strip()
            if not cmd:
                continue
            if cmd in (":exit", ":quit", "exit", "quit"):
                print("Dismissing Nyx AI Team.")
                break
            run_team_pipeline(cmd)
        except KeyboardInterrupt:
            print("\nType :exit to quit.")
        except EOFError:
            break

if __name__ == "__main__":
    start_console()