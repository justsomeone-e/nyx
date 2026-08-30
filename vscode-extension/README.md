# Nyx Language Toolchain

The official VS Code companion for `.nyx` and legacy `.he` files.

[GitHub Repository](https://github.com/justsomeone-e/nyx) ·
[Documentation](https://github.com/justsomeone-e/nyx#readme) ·
[Releases](https://github.com/justsomeone-e/nyx/releases) ·
[Compiler Roadmap](https://github.com/justsomeone-e/nyx/blob/main/docs/internals/ROADMAP_AND_BACKEND_GATES.md) ·
[Report an Issue](https://github.com/justsomeone-e/nyx/issues/new)

## What you get

- Syntax highlighting and canonical v4 completions
- LSP diagnostics, hover, completion, and go-to-definition
- One-click **Run**, **Build**, and **Check** commands
- Persistent integrated-terminal output, so native executables do not disappear after exit
- `Nyx: Toolchain Doctor` environment diagnostics
- Direct access to the repository, documentation, releases, roadmap, and issue reporter

## Quick actions

Open the Command Palette with `Ctrl+Shift+P` (`Cmd+Shift+P` on macOS), then run:

| Command | Purpose |
| --- | --- |
| `Nyx: Run Current File` | Compile and run the active source file. |
| `Nyx: Build Current File` | Build without losing terminal output. |
| `Nyx: Check Current File` | Parse and type-check without producing an artifact. |
| `Nyx: Toolchain Doctor` | Diagnose Nyx and native toolchain availability. |
| `Nyx: Open GitHub Repository` | Open the Nyx source repository. |
| `Nyx: Open Documentation` | Open the language and toolchain documentation. |
| `Nyx: Open Releases` | View published versions and release notes. |
| `Nyx: Open Compiler Roadmap` | Inspect backend maturity and RC gates. |
| `Nyx: Report an Issue` | Open a new GitHub issue. |

## Compiler discovery

By default, the extension prefers the canonical Nyx installation at
`~/.nyx/bin/nyx` (`nyx.cmd` on Windows) before searching `PATH`. Set
`nyx.server.path` when you deliberately want to use another compiler build.

## Target requirements

| Target | Host requirement |
| --- | --- |
| `hecpp` | Clang++, GCC/G++, or MSVC `cl` with C++20 support. |
| `hejs` | Node.js. |
| `hepy` | Python 3. |

Expose the native compiler on `PATH` or set `NYX_CXX`, then run
`Nyx: Toolchain Doctor` to verify the environment.

## Local installation

Open the generated `.vsix` file in VS Code, or run:

```text
code --install-extension nyx-language-support-<version>.vsix
```

No marketplace download is required for a local package. After upgrading the
extension or compiler, run **Developer: Reload Window** once so VS Code restarts
the Nyx language server with the new files.
