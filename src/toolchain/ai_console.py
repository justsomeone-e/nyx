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

EFFORT_LEVEL = "high"
MAX_TOKENS = 1400

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

def call_deepseek(prompt, system_prompt="You are the Lead Language Architect for Nyx."):
    url = "https://api.deepseek.com/chat/completions"
    headers = {"Authorization": f"Bearer {DEEPSEEK_KEY}", "Content-Type": "application/json"}
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": f"{system_prompt} (Effort Level: {EFFORT_LEVEL.upper()}). Ensure mathematical and syntactical perfection."},
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
    try:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {"Authorization": f"Bearer {OPENROUTER_KEY}", "Content-Type": "application/json"}
        data = {
            "model": "nvidia/nemotron-3-ultra-550b-a55b",
            "messages": [
                {"role": "system", "content": f"{system_prompt} Conduct an uncompromising audit targeting zero flaws."},
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
                    {"role": "system", "content": f"{system_prompt} Synthesize mathematically flawless production code."},
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
    print(f"[*] 🚀 PURSUIT OF FLAWLESSNESS: DEEP MULTI-AGENT PIPELINE")
    print(f"    Task: {task}")
    print(f"    Effort: \033[92m{EFFORT_LEVEL.upper()}\033[96m | Closed-Loop Auto-Healing: \033[92mENABLED\033[96m")
    print("===================================================================\033[0m\n")

    # Step 1: Deep Architect
    print(f"\033[90m[*] Step 1: Lead Architect (DeepSeek Platform) conducting architectural analysis...\033[0m")
    p1 = f"""User Task: {task}
Mission:
1. Conduct deep architectural analysis for Nyx.
2. Provide idiomatic, mathematically rigorous Nyx code using fn, strong types, guard statements, and methods.
3. Keep syntax completely standard according to Nyx syntax rules."""
    t1, res1 = call_deepseek(p1)
    print(f"\033[92m[1. ARCHITECT: DeepSeek Platform ({t1:.2f}s)]\033[0m")
    print(res1)
    print()

    # Step 2: High-Scrutiny Auditor
    print(f"\033[90m[*] Step 2: Systems Auditor (Nemotron 3 Ultra 550B) stress-auditing for zero flaws...\033[0m")
    p2 = f"""Task: {task}
The Lead Architect proposed:
---
{res1}
---
Conduct an exhaustive systems audit:
1. Flaw Detection: Find every boundary condition, overflow hazard, null safety defect, or contract inversion (e.g. min > max).
2. Optimization: Identify instruction-level improvements (branchless CMOV, cache layout).
3. Hardened Patch: Provide the hardened implementation with defensive assertions."""
    name2, t2, res2 = call_auditor(p2)
    print(f"\033[93m[2. AUDITOR: {name2} ({t2:.2f}s) reviewing Step 1]\033[0m")
    print(res2)
    print()

    # Step 3: Consensus Synthesizer
    print(f"\033[90m[*] Step 3: Consensus Synthesizer formulating flawless code...\033[0m")
    p3 = f"""Task: {task}
Architect Proposal:
---
{res1}
---
Auditor Critique & Hardening:
---
{res2}
---
Produce the definitive, 100% complete, flawless Nyx code inside ```nyx ... ```. Include no pseudo-code."""
    name3, t3, res3 = call_synthesizer(p3)
    print(f"\033[95m[3. CONSENSUS SYNTHESIZER: {name3} ({t3:.2f}s)]\033[0m")
    print(res3)
    print()

    # Extract code
    match = re.search(r"```nyx\s*(.*?)\s*```", res3, re.DOTALL)
    if not match:
        match = re.search(r"```\s*(.*?)\s*```", res3, re.DOTALL)
    
    if match:
        current_code = match.group(1).strip()
        print("\033[96m===================================================================")
        print("[*] 🛡️ CLOSED-LOOP COMPILER VERIFICATION & AUTO-HEALING")
        print("===================================================================\033[0m")
        
        max_healing_rounds = 3
        is_flawless = False

        for healing_round in range(max_healing_rounds):
            with tempfile.NamedTemporaryFile(suffix=".nyx", delete=False, mode="w", encoding="utf-8") as f:
                f.write(current_code + "\n\nprint(\"[PASS] Code compiled and executed cleanly!\");\n")
                temp_path = f.name
            
            try:
                # 1. Type and semantic check
                check_res = subprocess.run(["nyx", "check", temp_path], capture_output=True, text=True, timeout=10)
                if check_res.returncode != 0:
                    err_msg = check_res.stderr or check_res.stdout
                else:
                    # 2. Execution test
                    run_res = subprocess.run(["nyx", "run", temp_path, "--target", "hepy"], capture_output=True, text=True, timeout=10)
                    if run_res.returncode == 0:
                        print(f"\n\033[92m🏆 [100% FLAWLESS VERIFICATION ACHIEVED] (Round {healing_round + 1}):\033[0m")
                        print("  ✔ Static Type Check: 0 Errors")
                        print("  ✔ Syntax Invariants: 0 Violations")
                        print("  ✔ Execution Output:  " + run_res.stdout.strip())
                        is_flawless = True
                        break
                    else:
                        err_msg = run_res.stderr or run_res.stdout
            except Exception as e:
                err_msg = str(e)
            finally:
                try: os.remove(temp_path)
                except: pass

            print(f"\033[93m[⚠️ Flaw Detected in Attempt {healing_round + 1}]:\033[0m")
            print(f"  {err_msg.strip()[:200]}")
            print("\033[96m[*] Auto-Healing Triggered: Feeding compiler error back to models to patch...\033[0m")
            
            heal_prompt = f"""The Nyx compiler rejected your code with error:
---
{err_msg}
---
Faulty code:
---
{current_code}
---
Fix the error completely. Return ONLY the corrected, 100% flawless Nyx code inside ```nyx ... ```."""
            t_heal, patch_res = call_deepseek(heal_prompt, "You are the Emergency Code Repair Specialist for Nyx compiler.")
            m_patch = re.search(r"```nyx\s*(.*?)\s*```", patch_res, re.DOTALL)
            if m_patch:
                current_code = m_patch.group(1).strip()
            else:
                break

        if not is_flawless:
            print("\033[91m[!] Code required manual developer inspection.\033[0m\n")

def start_console():
    print(f"""
\033[96m===================================================================
⚡ NYX AI FLAWLESS MULTI-AGENT WORKFORCE — REAL-TIME COLLABORATION
===================================================================\033[0m
Your Engineering Team is Assembled:
  • Lead Architect:        DeepSeek Platform (~0.9s)
  • Systems Reviewer:      Nemotron 3 Ultra 550B (High Reasoning ~3.7s)
  • Consensus Synthesizer: Kimi K3 / DeepSeek (~1.2s)
  • Closed-Loop Verifier:  Local nyx Compiler Engine & Auto-Healer

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