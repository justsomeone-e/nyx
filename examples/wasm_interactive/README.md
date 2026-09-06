# Nyx WebAssembly Interactive Calculator

An interactive, zero-dependency browser application powered by a WebAssembly computation core written in Nyx (`calculator.nyx`).

## What It Demonstrates

- **Direct Nyx -> WebAssembly Compilation**: Fast mathematical and algorithmic routines compiled into a standalone `.wasm` binary.
- **ABI v1 ES Module Integration**: Clean JavaScript/TypeScript bindings (`bundle/calculator.mjs` and `bundle/calculator.d.ts`) generated automatically by `nyx bundle`.
- **Browser Interop**: Asynchronous module initialization with `await initNyxModule()`, seamless calling of exported Nyx functions from modern ES module scripts.

## Building the WASM Bundle

To rebuild the WebAssembly bundle:
```bash
nyx bundle calculator.nyx -o bundle --package
```

## Running the Web App

Start any local static HTTP server in this directory:
```bash
# Using Python
python -m http.server 8080

# Or using Node.js npx
npx serve .
```

Open `http://localhost:8080` in any modern web browser to interact with the Nyx WebAssembly core in real-time.
