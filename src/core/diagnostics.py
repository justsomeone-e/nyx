import sys
import os

class DiagnosticError(Exception):
    def __init__(self, code: str, title: str, filepath: str, line: int, col: int, formatted_msg: str):
        super().__init__(formatted_msg)
        self.code = code
        self.title = title
        self.filepath = filepath
        self.line = line
        self.col = col
        self.formatted_msg = formatted_msg

class DiagnosticEmitter:
    EXIT_ON_ERROR = True  # Can be disabled by test suites

    @classmethod
    def emit_error(
        cls,
        filepath: str,
        source: str,
        line: int,
        col: int,
        code: str,
        title: str,
        length: int = 1,
        expected: str = "",
        found: str = "",
        help_msg: str = "",
        searched: list = None,
        note: str = ""
    ):
        lines = source.splitlines() if source else []
        line_content = lines[line - 1] if 0 < line <= len(lines) else ""
        
        # Calculate caret span width
        caret_len = max(1, length)
        pointer = " " * max(0, col - 1) + "^" * caret_len

        out = []
        out.append(f"\n\033[91m\033[1merror[{code}]: {title}\033[0m")
        out.append(f"  \033[94m-->\033[0m {filepath}:{line}:{col}")
        out.append(f"   \033[94m|\033[0m")
        if line_content:
            out.append(f"\033[94m{line:2d} |\033[0m {line_content}")
            out.append(f"   \033[94m|\033[0m \033[91m{pointer}\033[0m")
            out.append(f"   \033[94m|\033[0m")
            
        if expected or found:
            if expected:
                out.append(f"   \033[94m=\033[0m \033[1mexpected:\033[0m \033[92m{expected}\033[0m")
            if found:
                out.append(f"   \033[94m=\033[0m \033[1mfound:   \033[0m \033[91m{found}\033[0m")
                
        if searched:
            out.append(f"   \033[94m=\033[0m \033[1msearched paths:\033[0m")
            for p in searched:
                out.append(f"       • {p}")
                
        if note:
            out.append(f"   \033[94m=\033[0m \033[93m\033[1mnote:\033[0m {note}")

        if help_msg:
            out.append(f"   \033[94m=\033[0m \033[96m\033[1mhelp:\033[0m {help_msg}")
            
        out.append("")
        formatted = "\n".join(out)
        print(formatted)
        
        if cls.EXIT_ON_ERROR:
            sys.exit(1)
        else:
            raise DiagnosticError(code, title, filepath, line, col, formatted)

    @classmethod
    def emit_warning(cls, filepath: str, line: int, col: int, code: str, msg: str, help_msg: str = ""):
        print(f"\033[93m\033[1mwarning[{code}]:\033[0m {msg} (at {filepath}:{line}:{col})")
        if help_msg:
            print(f"   \033[94m=\033[0m \033[96m\033[1mhelp:\033[0m {help_msg}")
