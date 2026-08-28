try:
    from .toolchain import (
        Formatter, Linter, Debugger, Profiler,
        DocGenerator, PackageManager, StandalonePackager
    )
except (ImportError, ValueError):
    from src.toolchain import (
        Formatter, Linter, Debugger, Profiler,
        DocGenerator, PackageManager, StandalonePackager
    )
