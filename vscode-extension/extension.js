const vscode = require('vscode');
const fs = require('fs');
const path = require('path');
const { LanguageClient } = require('vscode-languageclient/node');
const { createServerOptions } = require('./server_options');
const { registerNyxCommands } = require('./nyx_commands');
const languageSurface = require('./language-surface.json');

let languageClient;

async function activate(context) {
    const serverConfig = vscode.workspace.getConfiguration('nyx.server');
    if (serverConfig.get('enabled', true)) {
        const configuredPath = serverConfig.get('path', 'nyx');
        const serverOptions = createServerOptions(configuredPath);
        const clientOptions = {
            documentSelector: [
                { scheme: 'file', language: 'nyxlang' },
                { scheme: 'untitled', language: 'nyxlang' }
            ],
            outputChannelName: 'Nyx Language Server'
        };
        languageClient = new LanguageClient(
            'nyxLanguageServer',
            'Nyx Language Server',
            serverOptions,
            clientOptions
        );
        try {
            await languageClient.start();
            context.subscriptions.push({
                dispose: () => languageClient ? languageClient.stop() : undefined
            });
        } catch (error) {
            languageClient = undefined;
            console.warn(`Nyx language server could not start: ${error.message}`);
        }
    }

    registerNyxCommands(vscode, context);

    // ---------------------------------------------------------
    // 1. TOP PRIORITY NATIVE SYSTEM HEADERS (ALWAYS AT TOP)
    // ---------------------------------------------------------
    const priorityHeaders = [
        { name: "windows.h", cat: "Windows Win32 Native API", desc: "Core Windows OS SDK API, handles, messages, system calls" },
        { name: "winsock2.h", cat: "Windows Sockets 2", desc: "Windows network sockets and TCP/IP stack API" },
        { name: "ws2tcpip.h", cat: "Windows TCP/IP Extensions", desc: "getaddrinfo, IPv6 protocols, WinSock2 extensions" },
        { name: "unistd.h", cat: "Linux / POSIX Standard API", desc: "Standard symbolic constants and POSIX operating system API" },
        { name: "sys/socket.h", cat: "Linux / POSIX Sockets", desc: "Internet & UNIX domain socket communication" },
        { name: "sys/stat.h", cat: "Linux / POSIX File Status", desc: "File attributes, permissions, and directory inodes" },
        { name: "sys/types.h", cat: "Linux / POSIX Data Types", desc: "System data type definitions (pid_t, size_t, off_t)" },
        { name: "sys/time.h", cat: "Linux / POSIX Time API", desc: "gettimeofday, timeval, microsecond clock" },
        { name: "sys/mman.h", cat: "Linux / POSIX Memory Map", desc: "mmap, munmap, virtual memory management" },
        { name: "netinet/in.h", cat: "Linux / POSIX Networking", desc: "Internet protocol family, sockaddr_in structure" },
        { name: "arpa/inet.h", cat: "Linux / POSIX IP Address", desc: "inet_addr, inet_ntoa, IP conversion functions" },
        { name: "pthread.h", cat: "POSIX Multi-Threading", desc: "POSIX threads, mutexes, condition variables" },
        { name: "fcntl.h", cat: "POSIX / Linux File Control", desc: "File access modes, open(), fcntl() descriptors" },
        { name: "signal.h", cat: "POSIX / Linux Signals", desc: "Signal handling, SIGINT, SIGTERM, kill()" },
        { name: "dirent.h", cat: "POSIX / Linux Directory", desc: "Directory entry streams, opendir(), readdir()" },
        { name: "dlfcn.h", cat: "POSIX Dynamic Linking", desc: "dlopen, dlsym, dlclose dynamic library loading" },
        { name: "poll.h", cat: "POSIX Event Polling", desc: "poll(), synchronous I/O multiplexing" },
        { name: "sys/epoll.h", cat: "Linux High-Perf Epoll", desc: "epoll_create, epoll_ctl, epoll_wait I/O event notification" },
        { name: "iostream", cat: "C++ STL I/O Stream", desc: "std::cout, std::cin, std::endl" },
        { name: "vector", cat: "C++ STL Dynamic Array", desc: "std::vector<T> resizable array container" },
        { name: "string", cat: "C++ STL String", desc: "std::string UTF-8 text representation" },
        { name: "memory", cat: "C++ STL Smart Pointers", desc: "std::unique_ptr, std::shared_ptr, allocators" },
        { name: "chrono", cat: "C++ STL High-Res Time", desc: "std::chrono precision clocks, durations, time points" },
        { name: "thread", cat: "C++ STL Multi-Threading", desc: "std::thread, jthread, hardware concurrency" },
        { name: "cmath", cat: "C++ STL Math Functions", desc: "std::sin, std::cos, std::sqrt, std::pow" },
        { name: "cstdint", cat: "C++ Fixed Width Integers", desc: "int64_t, uint64_t, int32_t, uint8_t types" },
        { name: "algorithm", cat: "C++ STL Algorithms", desc: "std::sort, std::find, std::transform, ranges" },
        { name: "fstream", cat: "C++ STL File Streams", desc: "std::ifstream, std::ofstream disk file I/O" },
        { name: "sstream", cat: "C++ STL String Streams", desc: "std::stringstream, string formatting buffers" },
        { name: "stdio.h", cat: "C Standard Input/Output", desc: "printf, scanf, fopen, fread, fwrite" },
        { name: "stdlib.h", cat: "C Standard Utilities", desc: "malloc, free, exit, rand, atoi, system" }
    ];

    // ---------------------------------------------------------
    // 2. EXHAUSTIVE C++ STL & SYSTEM HEADER SET
    // ---------------------------------------------------------
    const defaultHeaders = [
        "any", "array", "atomic", "barrier", "bit", "bitset", "charconv",
        "compare", "complex", "concepts", "condition_variable", "coroutine",
        "deque", "expected", "filesystem", "flat_map", "flat_set", "format",
        "forward_list", "functional", "future", "initializer_list", "iomanip",
        "ios", "iosfwd", "istream", "iterator", "latch", "list", "map",
        "mdspan", "memory_resource", "mutex", "numbers", "numeric", "optional",
        "ostream", "print", "queue", "random", "ranges", "ratio", "regex",
        "scoped_allocator", "semaphore", "set", "shared_mutex", "source_location",
        "span", "spanstream", "stack", "stacktrace", "stdexcept", "stop_token",
        "streambuf", "string_view", "syncstream", "system_error", "tuple",
        "type_traits", "typeindex", "typeinfo", "unordered_map", "unordered_set",
        "utility", "valarray", "variant", "version",

        "cassert", "cctype", "cerrno", "cfenv", "cfloat", "cinttypes", "climits",
        "clocale", "csetjmp", "csignal", "cstdarg", "cstddef", "cstdio", "cstdlib",
        "cstring", "ctime", "cuchar", "cwchar", "cwctype",

        "windowsx.h", "mmsystem.h", "winuser.h", "wingdi.h", "winbase.h",
        "shellapi.h", "shlobj.h", "tlhelp32.h", "psapi.h", "dbghelp.h",
        "direct.h", "io.h", "conio.h", "process.h", "termios.h", "utime.h",
        "sys/wait.h", "sys/select.h", "sys/resource.h", "netinet/tcp.h",
        "netdb.h", "directxmath.h", "d3d12.h", "d3d11.h", "GL/gl.h", "vulkan/vulkan.h"
    ];

    const headerMap = new Map();
    // 1. Add priority headers first with top sortText (0000_)
    priorityHeaders.forEach((h, index) => {
        headerMap.set(h.name.toLowerCase(), {
            name: h.name,
            detail: `[${h.cat}] <${h.name}>`,
            doc: h.desc,
            sortText: `0000_${String(index).padStart(3, '0')}_${h.name}`
        });
    });

    // 2. Add remaining default headers
    defaultHeaders.forEach(h => {
        const key = h.toLowerCase();
        if (!headerMap.has(key)) {
            headerMap.set(key, {
                name: h,
                detail: `Header: <${h}>`,
                doc: `C/C++ Header \`<${h}>\``,
                sortText: `1000_${h}`
            });
        }
    });

    // 3. Optionally scan the explicitly configured native toolchain. Never
    // embed a developer-machine path in the extension package.
    const configuredCompiler = process.env.NYX_CXX || '';
    const includeRoots = [];
    if (configuredCompiler && path.isAbsolute(configuredCompiler)) {
        const toolchainRoot = path.resolve(path.dirname(configuredCompiler), '..');
        includeRoots.push(
            { directory: path.join(toolchainRoot, 'include', 'c++', 'v1'), category: 'C++ STL' },
            { directory: path.join(toolchainRoot, 'include'), category: 'System Header' }
        );
    }
    for (const root of includeRoots) {
        try {
            if (!fs.existsSync(root.directory)) continue;
            for (const file of fs.readdirSync(root.directory)) {
                const key = file.toLowerCase();
                const isWinRtNoise = (file.match(/\./g) || []).length > 1 && file.startsWith('windows.');
                const valid = root.category === 'C++ STL'
                    ? !file.startsWith('__') && !file.endsWith('.imp') && !file.endsWith('.modulemap')
                    : file.endsWith('.h') && !isWinRtNoise;
                if (valid && !headerMap.has(key)) {
                    headerMap.set(key, {
                        name: file,
                        detail: `[${root.category}] <${file}>`,
                        doc: `${root.category} \`<${file}>\``,
                        sortText: `${root.category === 'C++ STL' ? '2000' : '3000'}_${file}`
                    });
                }
            }
        } catch (_error) {
            // Header scanning is optional; canonical static completions remain available.
        }
    }

    // ---------------------------------------------------------
    // 3. STANDARD NYX MODULES & COMPILER TARGETS
    // ---------------------------------------------------------
    const stdModules = [
        { name: 'std/io', desc: 'Console I/O streams and formatting' },
        { name: 'std/fs', desc: 'File system operations (read, write, exists, remove)' },
        { name: 'std/math', desc: 'Mathematical functions (pow, sqrt, sin, cos, PI)' },
        { name: 'std/time', desc: 'High-resolution timers and delay_ms()' },
        { name: 'std/memory', desc: 'Low-level pointers, addr(), peek(), poke(), memdump()' },
        { name: 'std/os', desc: 'Operating system interop, platform info, env variables' },
        { name: 'std/net', desc: 'TCP/IP sockets and networking streams' },
        { name: 'std/gpio', desc: 'Microcontroller GPIO pin control' },
        { name: 'std/board', desc: 'Selected Nucleo connector and custom-board pin aliases' },
        { name: 'std/serial', desc: 'UART serial communication port API' },
        { name: 'std/spi', desc: 'SPI bus hardware communication' },
        { name: 'std/i2c', desc: 'I2C two-wire hardware interface' },
        { name: 'std/adc', desc: '12-bit analog input conversion' },
        { name: 'std/pwm', desc: 'Timer-backed PWM output' },
        { name: 'std/timer', desc: 'General-purpose hardware timers' },
        { name: 'std/interrupt', desc: 'Cortex-M NVIC interrupt control' },
        { name: 'std/mmio', desc: 'Volatile register access and masked updates' },
        { name: 'std/process', desc: 'Child process execution' },
        { name: 'std/str', desc: 'Advanced string manipulation and Unicode' },
        { name: 'std/platform', desc: 'Hardware architecture detection' },
        { name: 'std/env', desc: 'Environment configuration access' }
    ];

    const targetsList = [
        { name: 'hecpp', desc: 'C++20 High Performance Native Binary (Clang/GCC)' },
        { name: 'heasm', desc: 'x86_64 Intel Assembly Source (.s) with LLVM Optimizations' },
        { name: 'hereact', desc: 'React 19 Reactive UI Components & Hooks (.tsx)' },
        { name: 'hejs', desc: 'Node.js ES2022 JavaScript ESM Module' },
        { name: 'hers', desc: 'Rust 2021 Safe Systems Conformance Target' },
        { name: 'hepy', desc: 'Python 3 Rapid Scripting & Reference Semantics' },
        { name: 'hewasm', desc: 'WebAssembly (WASM/WAT) Binary Stack Engine' },
        { name: 'stm32f4', desc: 'Freestanding STM32F4 ELF / HEX / BIN firmware' }
    ];

    // ---------------------------------------------------------
    // 4. COMPLETION PROVIDER
    // ---------------------------------------------------------
    const completionProvider = vscode.languages.registerCompletionItemProvider(
        ['nyxlang', 'nyx', 'he', 'holyeasylang'],
        {
            provideCompletionItems(document, position, token, completionContext) {
                const items = [];
                const lineText = document.lineAt(position).text;
                const linePrefix = lineText.substring(0, position.character);
                const fullText = document.getText();

                let currentTarget = 'hecpp';
                const targetMatch = fullText.match(/^\s*#target\s+([a-zA-Z0-9_]+)/m);
                if (targetMatch) {
                    currentTarget = targetMatch[1].toLowerCase();
                }
                const hasNative = /#native\b/.test(fullText) || /unsafe\b/.test(fullText);

                function addSnippet(label, snippetText, detail, doc, kind = vscode.CompletionItemKind.Snippet) {
                    const item = new vscode.CompletionItem(label, kind);
                    item.insertText = new vscode.SnippetString(snippetText);
                    item.detail = detail;
                    item.documentation = new vscode.MarkdownString(doc);
                    items.push(item);
                }

                // 1. #native include <
                if (/#native\s+include/i.test(linePrefix)) {
                    const openIdx = linePrefix.lastIndexOf('<');
                    headerMap.forEach((hInfo) => {
                        const item = new vscode.CompletionItem(hInfo.name, vscode.CompletionItemKind.Module);
                        if (openIdx !== -1) {
                            item.range = new vscode.Range(new vscode.Position(position.line, openIdx), position);
                            item.insertText = `<${hInfo.name}>`;
                        } else {
                            item.insertText = ` <${hInfo.name}>`;
                        }
                        item.detail = hInfo.detail;
                        item.documentation = new vscode.MarkdownString(`### \`<${hInfo.name}>\`\n\n${hInfo.doc}`);
                        item.sortText = hInfo.sortText;
                        items.push(item);
                    });
                    return items;
                }

                // 2. #native (space)
                if (/#native\s*$/i.test(linePrefix)) {
                    addSnippet('include', 'include <${1:windows.h}>', '#native include <header>', 'Includes native C/C++ header.');
                    addSnippet('link', 'link "${1|ws2_32,user32,gdi32,pthread,dl,m|}"', '#native link "library"', 'Links system library.');
                    addSnippet('raw', 'raw {\n\t${0:// raw C++20 code}\n}', '#native raw { ... }', 'Direct inline C++ code injection block.');
                    addSnippet('use', 'use "${1|namespace std,std::chrono,std::string_view|}";', '#native use "namespace"', 'Injects C++ using namespace declaration.');
                    return items;
                }

                // 3. #target (space)
                if (/#target\s*$/i.test(linePrefix)) {
                    targetsList.forEach(t => {
                        const item = new vscode.CompletionItem(t.name, vscode.CompletionItemKind.EnumMember);
                        item.insertText = t.name;
                        item.detail = `Target: ${t.desc}`;
                        items.push(item);
                    });
                    return items;
                }

                // 4. import / use (space)
                if (/(?:import|use)\s+["']?$/i.test(linePrefix) || /(?:import|use)\s+["']std\/$/i.test(linePrefix)) {
                    stdModules.forEach(m => {
                        const item = new vscode.CompletionItem(m.name, vscode.CompletionItemKind.Module);
                        item.insertText = `"${m.name}";`;
                        item.detail = `nyx stdlib: ${m.name}`;
                        item.documentation = new vscode.MarkdownString(`**${m.name}**\n\n${m.desc}`);
                        items.push(item);
                    });
                    return items;
                }

                // Top level directives
                addSnippet('#target', '#target ${1|hecpp,heasm,hereact,hejs,hers,hepy,hewasm|}', 'Target Directive', 'Sets compilation backend target.');
                addSnippet('#native include', '#native include <${1:windows.h}>', 'Native Include', 'Includes C/C++ header.');
                addSnippet('#native link', '#native link "${1|ws2_32,user32,gdi32,pthread,dl,m|}"', 'Native Link', 'Links system library.');
                addSnippet('#native raw', '#native raw {\n\t${0:// raw C++20 code}\n}', 'Native Raw Block', 'Injects raw C++ code.');
                addSnippet('#native use', '#native use "${1|namespace std,std::chrono,std::string_view|}";', 'Native Use Directive', 'Namespace declaration.');

                // Core keywords
                addSnippet('fn', 'fn ${1:name}(${2:params}) -> ${3:type} {\n\t${0:// body}\n\treturn ${4:result};\n}', 'Function Definition', 'Declares a strongly-typed function.');
                addSnippet('struct', 'struct ${1:Name} {\n\t${2:field}: ${3:type}\n}', 'Struct Definition', 'Declares a custom data structure.');
                addSnippet('impl', 'impl ${1:StructName} {\n\tfn ${2:method_name}(self${3:, params}) -> ${4:type} {\n\t\t${0:// method body}\n\t}\n}', 'Impl Block', 'Implements methods for a struct.');
                addSnippet('var', 'var ${1:name} = ${2:value};', 'Mutable Variable', 'Declares a mutable variable.');
                addSnippet('const', 'const ${1:NAME} = ${2:value};', 'Constant', 'Declares an immutable constant.');
                addSnippet('if', 'if ${1:condition} {\n\t${0:// then branch}\n}', 'If Block', 'Conditional branch.');
                addSnippet('ifelse', 'if ${1:condition} {\n\t${2:// true branch}\n} else {\n\t${0:// false branch}\n}', 'If-Else Block', 'Two-way conditional branch.');
                addSnippet('for', 'for ${1:i} in ${2:0}..${3:count}-1 {\n\t${0:// loop body}\n}', 'For Range Loop', 'Iterates over a contiguous range.');
                addSnippet('while', 'while ${1:condition} {\n\t${0:// loop body}\n}', 'While Loop', 'Iterates while condition is true.');
                addSnippet('continue', 'continue;', 'Continue Statement', 'Skips to next loop iteration.');
                addSnippet('break', 'break;', 'Break Statement', 'Terminates loop.');
                addSnippet('defer', 'defer ${1:cleanup_expression};', 'Defer Statement', 'Executes cleanup expression on scope exit (LIFO).');
                addSnippet('guard', 'guard ${1:condition} else {\n\t${0:return;}\n}', 'Guard Statement', 'Early-exit safety guard block.');
                addSnippet('pipe', '|> ${1:func_name}', 'Pipeline Operator', 'Pipes expression forward as the first argument.');
                addSnippet('return', 'return ${1:result};', 'Return Statement', 'Returns from function.');
                addSnippet('throw', 'throw ${1:error};', 'Throw Statement', 'Terminates the current path and transfers control to the nearest catch block.');
                addSnippet('async fn', 'async fn ${1:name}(${2:params}) -> ${3:type} {\n\t${0:// body}\n}', 'Async Function', 'Declares a function that returns Task<T>.');
                addSnippet('await', 'await ${1:task}', 'Await Expression', 'Suspends until a Task<T> resolves and produces T.');
                addSnippet('match', 'match ${1:expr} {\n\t${2:pattern} => ${3:result},\n\t"_" => ${0:default}\n}', 'Pattern Matching', 'Pattern matching block.');
                addSnippet('print', 'print(${1:expr});', 'Print to Console', 'Prints expressions to stdout.');
                addSnippet('import', 'import "${1:std/io}";', 'Import Module', 'Imports standard library or local module.');
                addSnippet('use', 'use "${1:std/io}";', 'Use Module', 'Imports standard library or local module.');
                addSnippet('test', 'test "${1:test title}" {\n\tassert(${2:condition}, "${3:failure message}");\n}', 'Unit Test Block', 'Defines an automated in-file unit test.');
                addSnippet('assert', 'assert(${1:condition}, "${2:message}");', 'Assertion', 'Asserts condition is true; halts on failure.');

                if (currentTarget === 'stm32f4' || currentTarget === 'stm32' || currentTarget === 'embedded') {
                    addSnippet('volatile var', 'volatile var ${1:ticks}: ${2:u32} = ${3:0};', 'Volatile Embedded Storage', 'Declares storage observed by hardware or an interrupt handler.');
                    addSnippet('interrupt fn', 'interrupt fn ${1:TIM3_IRQHandler}() -> void {\n\t${2:timer_clear_update(3)};\n\t${0}\n}', 'Hardware Interrupt Handler', 'Declares a profile-validated Cortex-M interrupt handler.');
                    addSnippet('critical', 'critical {\n\t${0:// atomic register or shared-state update}\n}', 'Interrupt-Masked Scope', 'Masks interrupts and restores the previous PRIMASK state on every exit path.');
                    addSnippet('Buffer', 'var ${1:packet}: Buffer<${2:u8}, ${3:64}> = [${0}];', 'Fixed Embedded Buffer', 'Declares allocation-free fixed-capacity storage for UART, SPI, I²C, and DMA.');
                    addSnippet('buffer_ptr', 'buffer_ptr(${1:buffer})', 'Buffer Data Pointer', 'Returns the stable data address of a fixed Buffer for typed HAL calls.', vscode.CompletionItemKind.Function);
                    addSnippet('board_pin', 'board_pin("${1|LED,BUTTON,D0,D1,D2,D3,D4,D5,D6,D7,D8,D9,D10,D11,D12,D13,D14,D15,A0,A1,A2,A3,A4,A5,I2C_SDA,I2C_SCL|}")', 'Board Connector Alias', 'Resolves a pin from the selected --board profile.', vscode.CompletionItemKind.Function);
                }

                // Target specifics
                if (currentTarget === 'hereact' || currentTarget === 'react') {
                    addSnippet('useState', 'var [${1:state}, set${1/(.*)/${1:/capitalize}/}] = useState(${2:initialValue});', 'React useState Hook', 'Reactive state variable with updater.', vscode.CompletionItemKind.Function);
                    addSnippet('useEffect', 'useEffect(() => {\n\t${0:// side effect}\n}, [${1:deps}]);', 'React useEffect Hook', 'Component lifecycle side-effect hook.', vscode.CompletionItemKind.Function);
                    addSnippet('useRef', 'var ${1:ref} = useRef(${2:null});', 'React useRef Hook', 'Persistent mutable reference.', vscode.CompletionItemKind.Function);
                }

                if (currentTarget === 'hecpp' || currentTarget === 'heasm' || hasNative) {
                    addSnippet('unsafe', 'unsafe {\n\tvar ptr = addr(${1:variable});\n\tvar val = peek(ptr);\n\t${0}\n}', 'Unsafe Memory Block', 'Permits direct pointer arithmetic and dereferencing.');
                    addSnippet('addr', 'addr(${1:variable})', 'Get Pointer Address', 'Returns 64-bit physical memory address of variable.', vscode.CompletionItemKind.Function);
                    addSnippet('peek', 'peek(${1:ptr})', 'Read Memory Address', 'Dereferences 64-bit value at raw address.', vscode.CompletionItemKind.Function);
                    addSnippet('poke', 'poke(${1:ptr}, ${2:value})', 'Write Memory Address', 'Writes 64-bit value directly to memory address.', vscode.CompletionItemKind.Function);
                    addSnippet('memdump', 'memdump(${1:ptr}, ${2:num_bytes});', 'Hex Memory Dump', 'Dumps raw memory bytes formatted in hexadecimal.', vscode.CompletionItemKind.Function);
                    addSnippet('delay_ms', 'delay_ms(${1:1000});', 'High-Res Sleep', 'Thread sleep with microsecond precision.', vscode.CompletionItemKind.Function);
                }

                // Keep offline/editor completion as broad as the stable
                // compiler surface. Rich snippets above win when available;
                // plain keyword/type/runtime entries fill every remaining gap.
                const existingLabels = new Set(items.map(item => item.label));
                function addSurfaceItem(label, kind, detail, documentation) {
                    if (existingLabels.has(label)) return;
                    const item = new vscode.CompletionItem(label, kind);
                    item.detail = detail;
                    item.documentation = new vscode.MarkdownString(documentation);
                    items.push(item);
                    existingLabels.add(label);
                }
                languageSurface.stableKeywords.forEach(keyword => {
                    addSurfaceItem(
                        keyword,
                        vscode.CompletionItemKind.Keyword,
                        'Nyx stable keyword',
                        'Supported by the stable Nyx frontend language surface.'
                    );
                });
                languageSurface.experimentalKeywords.forEach(keyword => {
                    addSurfaceItem(
                        keyword,
                        vscode.CompletionItemKind.Keyword,
                        'Nyx experimental keyword',
                        'Frontend support exists, but cross-target semantics are not stable yet.'
                    );
                });
                languageSurface.builtinNames.forEach(name => {
                    addSurfaceItem(name, vscode.CompletionItemKind.Function, 'Nyx core runtime', 'Nyx core runtime function.');
                });
                languageSurface.typeNames.forEach(name => {
                    addSurfaceItem(name, vscode.CompletionItemKind.TypeParameter, 'Nyx type', 'Nyx language type.');
                });

                return items;
            }
        },
        '#', ' ', '<', '"', '/', ':', '.', 'i', 'u', 's', 'c', 'v', 'f', 'w'
    );

    context.subscriptions.push(completionProvider);
}

async function deactivate() {
    if (languageClient) {
        await languageClient.stop();
        languageClient = undefined;
    }
}

module.exports = {
    activate,
    deactivate
};
