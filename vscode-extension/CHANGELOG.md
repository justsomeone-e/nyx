# Change Log

## 4.0.0-dev.2

- Removed STM32/Nucleo/freestanding targets and their board completions.
- Removed the obsolete `volatile`, `interrupt`, `critical`, `Buffer<T, N>`, and
  `buffer_ptr` language surface.
- Synced syntax highlighting, snippets, LSP completions, and the canonical
  43-keyword compiler catalog.

## 4.0.0-dev.1

- Added one-click Run, Build, Check, and Toolchain Doctor commands.
- Run and Build now use VS Code's persistent integrated task terminal.
- Synchronized completions, snippets, icons, and LSP startup with the v4 language surface.
- Promoted the visible extension identity to **Nyx Language Toolchain** and
  replaced the undersized dark marketplace mark with a larger transparent icon.
- Added manifest-level homepage, issue tracker, and gallery metadata.
- Added Command Palette links for GitHub, documentation, releases, the compiler
  roadmap, and issue reporting.
- Prefer the canonical `~/.nyx/bin/nyx` installation before `PATH` to avoid
  accidentally launching an older language server shim.
