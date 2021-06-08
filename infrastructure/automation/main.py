import os
import subprocess
from pulumi import automation as auto

stack_name = "dev"

work_dir = os.path.join(os.path.dirname(__file__), "..", "src")

print("Preparing pulumi environment")

subprocess.run(
    ["python3", "-m", "venv", "venv"], check=True, cwd=work_dir, capture_output=True
)
subprocess.run(
    [
        os.path.join("venv", "bin", "python3"),
        "-m",
        "pip",
        "install",
        "--upgrade",
        "pip",
    ],
    check=True,
    cwd=work_dir,
    capture_output=True,
)
subprocess.run(
    [os.path.join("venv", "bin", "pip"), "install", "-r", "requirements.txt"],
    check=True,
    cwd=work_dir,
    capture_output=True,
)

stack = auto.create_or_select_stack(stack_name="dev", work_dir=work_dir)

stack.set_config("aws:region", auto.ConfigValue(value="us-east-1"))

stack_preview = stack.up(on_output=print)

subprocess.run(
    ["pulumi", "stack", "export", "--file", "stack.json"],
    check=True,
    cwd=work_dir,
    capture_output=True,
)

work_dir = os.path.join(os.path.dirname(__file__), "..", "diagrams")


print("Preparing diagrams environment")

subprocess.run(
    ["python3", "-m", "venv", "venv"], check=True, cwd=work_dir, capture_output=True
)
subprocess.run(
    [
        os.path.join("venv", "bin", "python3"),
        "-m",
        "pip",
        "install",
        "--upgrade",
        "pip",
    ],
    check=True,
    cwd=work_dir,
    capture_output=True,
)
subprocess.run(
    [os.path.join("venv", "bin", "pip"), "install", "-r", "requirements.txt"],
    check=True,
    cwd=work_dir,
    capture_output=True,
)

subprocess.run(
    [os.path.join("venv", "bin", "python3"), "diagrams_generator.py"],
    check=True,
    cwd=work_dir,
    capture_output=True,
)
