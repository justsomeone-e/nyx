import sys
import os

# Legacy bridge to src/compiler.py
sys.path.insert(0, os.path.dirname(__file__))
from src.compiler import Compiler

def main():
    if len(sys.argv) < 2:
        print("Usage: python he_compiler.py [build|run] <source.he> [--target hecpp|hereact|hepy|hejs|hewasm]")
        sys.exit(1)
    
    args = sys.argv[1:]
    run_immediately = True
    if args[0] in ("build", "run"):
        run_immediately = (args[0] == "run")
        args = args[1:]

    if not args:
        print("Error: Missing file argument.")
        sys.exit(1)

    filepath = args[0]
    target = None
    if "--target" in args:
        target = args[args.index("--target") + 1]

    Compiler(filepath, target_override=target).compile(run_immediately=run_immediately)

if __name__ == "__main__":
    main()
