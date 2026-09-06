# Nyx Package & Foreign Binding Consumer Example

This example demonstrates how a Nyx project:
1. Declares and resolves a local package dependency (`stats_core`) via `nyx.toml`.
2. Generates and verifies a deterministic lockfile (`nyx.lock`) with cryptographic SHA256 integrity checksums.
3. Consumes exported algorithms and functions from the package.
4. Consumes foreign C++ platform bindings (`std::filesystem`) with type safety.

## Directory Structure

```
package_consumer/
├── nyx.toml               # Project manifest declaring stats_core dependency
├── nyx.lock               # Deterministic lockfile with package checksums
├── README.md              # Documentation and execution guide
├── packages/
│   └── stats_core/        # Local package dependency
│       ├── nyx.toml       # stats_core manifest
│       └── src/
│           └── stats.nyx  # stats_core algorithms (clamp, sum_ints, max_int)
└── src/
    └── main.nyx           # Application consuming package and foreign bindings
```

## Running the Example

### Inspect Manifest & Dependencies
```bash
nyx pkg
```

### Verify Deterministic Lockfile
```bash
nyx install
```

### Compile & Execute
```bash
nyx run src/main.nyx
```
