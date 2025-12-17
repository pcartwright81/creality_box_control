🐍 Python Coding Standards
The following rules are mandatory for all Python code. Gemini must adhere to these standards when generating or modifying code:

Modern Python: Generate code strictly using modern Python standards (e.g., use pathlib for file system operations over os.path).

Type Hinting: All functions must include comprehensive type annotations for every argument and the return value (for example, def calculate_bmi(weight: float, height: float) -> float:).

Linter Compliance: All generated code must be compliant with the project's Ruff configuration standards. Do not include explanatory comments for standard or obvious code patterns.

Code Quality: The code must pass all type checks when analyzed by Pylance (using basic or strict mode).