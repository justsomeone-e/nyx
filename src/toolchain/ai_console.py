import urllib.request
import json
import time
import os
import sys
from concurrent.futures import ThreadPoolExecutor

def get_env_var(name):
    v = os.getenv(name)
    if v: return v
    # Try current directory .env or ~/.nyx/.env
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

def query_nim(key, model, prompt, max_tokens=250):
    if not key:
        return (0.0, "[!] NVIDIA API key not found. Set NVIDIA_KIMI_KEY or NVIDIA_NEMOTRON_KEY in .env")
    url = "https://integrate.api.nvidia.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    data = {"model": model, "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens}
    t0 = time.time()
    req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            out = json.loads(res.read().decode("utf-8"))
            msg = out["choices"][0]["message"]
            ans = msg.get("content") or msg.get("reasoning_content") or ""
            return (time.time() - t0, ans.strip())
    except Exception as e:
        return (time.time() - t0, f"Error: {e}")

def query_deepseek_platform(prompt, max_tokens=250):
    if not DEEPSEEK_KEY:
        return (0.0, "[!] DEEPSEEK_API_KEY not found in .env")
    url = "https://api.deepseek.com/chat/completions"
    headers = {"Authorization": f"Bearer {DEEPSEEK_KEY}", "Content-Type": "application/json"}
    data = {"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens}
    t0 = time.time()
    req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as res:
            out = json.loads(res.read().decode("utf-8"))
            return (time.time() - t0, out["choices"][0]["message"]["content"].strip())
    except Exception as e:
        return (time.time() - t0, f"Error: {e}")

def query_openrouter(prompt, max_tokens=250):
    if not OPENROUTER_KEY:
        return (0.0, "[!] OPENROUTER_API_KEY not found in .env")
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENROUTER_KEY}", "Content-Type": "application/json"}
    data = {"model": "deepseek/deepseek-chat", "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens}
    t0 = time.time()
    req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as res:
            out = json.loads(res.read().decode("utf-8"))
            return (time.time() - t0, out["choices"][0]["message"]["content"].strip())
    except Exception as e:
        return (time.time() - t0, f"Error: {e}")

def query_all(prompt):
    print("\n\033[96m[*] Firing prompt to all active models in parallel...\033[0m")
    tasks = [
        ("DeepSeek Platform (~0.8s)", lambda: query_deepseek_platform(prompt)),
        ("Kimi K3 (Nvidia NIM ~3.2s)", lambda: query_nim(KIMI_KEY, "moonshotai/kimi-k3", prompt)),
        ("Nemotron 3 Ultra 550B (Nvidia NIM ~7.4s)", lambda: query_nim(NEMOTRON_KEY, "nvidia/nemotron-3-ultra-550b-a55b", prompt)),
        ("OpenRouter DeepSeek (~3.5s)", lambda: query_openrouter(prompt))
    ]
    with ThreadPoolExecutor(max_workers=4) as ex:
        futures = {name: ex.submit(fn) for name, fn in tasks}
        for name, f in futures.items():
            elapsed, res = f.result()
            print(f"\n\033[92m===================================================================")
            print(f"[*] {name} ({elapsed:.2f}s):")
            print(f"===================================================================\033[0m")
            print(res)

def start_console():
    print("""
\033[96m===================================================================
⚡ NYX AI COMMAND CONSOLE — USER DIRECT CONTROL
===================================================================\033[0m
Direct Access to Your 4 AI Engineering Engines:
  1. DeepSeek Platform (Ultra Fast ~0.8s)
  2. Kimi K3 (Nvidia NIM ~3.2s)
  3. Nemotron 3 Ultra 550B (Nvidia NIM ~7.4s)
  4. OpenRouter DeepSeek (~3.5s)
  5. ⚡ ROUND-TABLE (Send to ALL 4 models simultaneously)

Type ':model <1-5>' to switch mode.
Type ':exit' to quit.
""")
    mode = "5"
    names = {
        "1": "DeepSeek Platform",
        "2": "Kimi K3",
        "3": "Nemotron 3 Ultra",
        "4": "OpenRouter DeepSeek",
        "5": "⚡ ROUND-TABLE (ALL)"
    }

    while True:
        try:
            prompt_str = f"\033[93mnyx-ai [{names[mode]}]>\033[0m "
            cmd = input(prompt_str).strip()
            if not cmd:
                continue
            if cmd in (":exit", ":quit", "exit", "quit"):
                print("Exiting Nyx AI Console.")
                break
            if cmd.startswith(":model"):
                parts = cmd.split()
                if len(parts) > 1 and parts[1] in names:
                    mode = parts[1]
                    print(f"\033[92m[OK] Switched active model to: {names[mode]}\033[0m")
                else:
                    print("Usage: :model <1|2|3|4|5>")
                continue
            
            if mode == "5":
                query_all(cmd)
            elif mode == "1":
                elapsed, res = query_deepseek_platform(cmd)
                print(f"\n\033[92m[DeepSeek Platform ({elapsed:.2f}s)]:\033[0m\n{res}\n")
            elif mode == "2":
                elapsed, res = query_nim(KIMI_KEY, "moonshotai/kimi-k3", cmd)
                print(f"\n\033[92m[Kimi K3 ({elapsed:.2f}s)]:\033[0m\n{res}\n")
            elif mode == "3":
                elapsed, res = query_nim(NEMOTRON_KEY, "nvidia/nemotron-3-ultra-550b-a55b", cmd)
                print(f"\n\033[92m[Nemotron 3 Ultra ({elapsed:.2f}s)]:\033[0m\n{res}\n")
            elif mode == "4":
                elapsed, res = query_openrouter(cmd)
                print(f"\n\033[92m[OpenRouter DeepSeek ({elapsed:.2f}s)]:\033[0m\n{res}\n")

        except KeyboardInterrupt:
            print("\nType :exit to quit.")
        except EOFError:
            break

if __name__ == "__main__":
    start_console()