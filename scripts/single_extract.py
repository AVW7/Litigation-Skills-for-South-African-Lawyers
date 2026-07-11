import sys
import importlib

# Ensure hermes package is in sys.path
sys.path.append("/Users/ajadvanwyk/.hermes/hermes-agent")

if __name__ == "__main__":
    # Read the full prompt from stdin
    prompt = sys.stdin.read()
    
    try:
        # Dynamically import to satisfy static checkers/linters in the workspace
        oneshot_module = importlib.import_module("hermes_cli.oneshot")
        run_oneshot = oneshot_module.run_oneshot
    except ImportError as e:
        print(f"ImportError: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Run the oneshot execution
    exit_code = run_oneshot(prompt=prompt)
    sys.exit(exit_code)
