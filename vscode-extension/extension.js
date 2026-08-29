const vscode = require('vscode');
const fs = require('fs');
const path = require('path');

function activate(context) {
    // ---------------------------------------------------------
    // 1. DISCOVER ALL C++ HEADERS DYNAMICALLY & EXHAUSTIVELY
    // ---------------------------------------------------------
    const defaultCppHeaders = [
        // Containers & Iterators
        "algorithm", "any", "array", "bitset", "deque", "flat_map", "flat_set", "forward_list",
        "iterator", "list", "map", "mdspan", "queue", "ranges", "set", "span", "stack",
        "unordered_map", "unordered_set", "vector",

        // Utilities, Memory & Functional
        "bit", "chrono", "compare", "concepts", "coroutine", "expected", "functional",
        "initializer_list", "memory", "memory_resource", "optional", "ratio", "scoped_allocator",
        "source_location", "stacktrace", "tuple", "type_traits", "typeindex", "typeinfo",
        "utility", "variant", "version",

        // Strings, Text & Formatting
        "charconv", "format", "print", "regex", "string", "string_view", "text_encoding",

        // Streams & I/O
        "filesystem", "fstream", "iomanip", "ios", "iosfwd", "iostream", "istream",
        "ostream", "spanstream", "sstream", "streambuf", "syncstream", "strstream",

        // Numerics & Math
        "cmath", "complex", "numbers", "numeric", "random", "valarray",

        // Concurrency & Multi-Threading
        "atomic", "barrier", "condition_variable", "future", "latch", "mutex",
        "semaphore", "shared_mutex", "stop_token", "thread",

        // C Standard Library Wrappers
        "cassert", "cctype", "cerrno", "cfenv", "cfloat", "cinttypes", "climits",
        "clocale", "cmath", "csetjmp", "csignal", "cstdarg", "cstddef", "cstdint",
        "cstdio", "cstdlib", "cstring", "ctime", "cuchar", "cwchar", "cwctype",

        // Low-Level, OS & Windows APIs
        "windows.h", "winsock2.h", "ws2tcpip.h", "windowsx.h", "direct.h", "io.h",
        "fcntl.h", "conio.h", "process.h", "pthread.h", "sys/stat.h", "sys/types.h",
        "unistd.h", "directxmath.h", "d3d12.h", "d3d11.h", "GL/gl.h", "vulkan/vulkan.h"
    ];

    // Attempt to load live headers from installed MinGW compiler
    const headerSet = new Set(defaultCppHeaders);
    const minGwDir = "C:\\Users\\USER\\AppData\\Local\\Microsoft\\WinGet\\Packages\\MartinStorsjo.LLVM-MinGW.UCRT_Microsoft.Winget.Source_8wekyb3d8bbwe\\llvm-mingw-20260616-ucrt-x86_64";
    const stlDir = path.join(minGwDir, "include", "c++", "v1");
    const sysIncDir = path.join(minGwDir, "include");

    try {
        if (fs.existsSync(stlDir)) {
            const files = fs.readdirSync(stlDir);
            for (const f of files) {
                if (!f.startsWith("__") && !f.endsWith(".imp") && !f.endsWith(".modulemap")) {
                    headerSet.add(f);
                }
            }
        }
        if (fs.existsSync(sysIncDir)) {
            const files = fs.readdirSync(sysIncDir);
            for (const f of files) {
                if (f.endsWith(".h")) {
                    headerSet.add(f);
                }
            }
        }
    } catch (e) {}

    const allHeaders = Array.from(headerSet).sort();

    // ---------------------------------------------------------
    // 2. STANDARD NYX MODULES & COMPILER TARGETS
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
        { name: 'std/serial', desc: 'UART serial communication port API' },
        { name: 'std/spi', desc: 'SPI bus hardware communication' },
        { name: 'std/i2c', desc: 'I2C two-wire hardware interface' },
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
        { name: 'hewasm', desc: 'WebAssembly (WASM/WAT) Binary Stack Engine' }
    ];

    // ---------------------------------------------------------
    // 3. COMPLETION PROVIDER WITH COMPLETE C++ HEADER CATALOG
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

                // 1. #native include < (Search through entire C++ repository of headers)
                if (/#native\s+include/i.test(linePrefix)) {
                    const hasOpenBracket = linePrefix.includes('<');
                    allHeaders.forEach(h => {
                        const item = new vscode.CompletionItem(h, vscode.CompletionItemKind.Module);
                        item.insertText = hasOpenBracket ? `${h}>` : `<${h}>`;
                        item.detail = `Header: <${h}>`;
                        item.documentation = new vscode.MarkdownString(`C/C++ Header \`<${h}>\``);
                        items.push(item);
                    });
                    return items;
                }

                // 2. #native (space)
                if (/#native\s*$/i.test(linePrefix)) {
                    addSnippet('include', 'include <${1:iostream}>', '#native include <header>', 'Includes native C/C++ header.');
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
                addSnippet('#native include', '#native include <${1:iostream}>', 'Native Include', 'Includes C/C++ header.');
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
                addSnippet('return', 'return ${1:result};', 'Return Statement', 'Returns from function.');
                addSnippet('match', 'match ${1:expr} {\n\t${2:pattern} => ${3:result},\n\t"_" => ${0:default}\n}', 'Pattern Matching', 'Pattern matching block.');
                addSnippet('print', 'print(${1:expr});', 'Print to Console', 'Prints expressions to stdout.');
                addSnippet('import', 'import "${1:std/io}";', 'Import Module', 'Imports standard library or local module.');
                addSnippet('use', 'use "${1:std/io}";', 'Use Module', 'Imports standard library or local module.');
                addSnippet('test', 'test "${1:test title}" {\n\tassert(${2:condition}, "${3:failure message}");\n}', 'Unit Test Block', 'Defines an automated in-file unit test.');
                addSnippet('assert', 'assert(${1:condition}, "${2:message}");', 'Assertion', 'Asserts condition is true; halts on failure.');

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

                return items;
            }
        },
        '#', ' ', '<', '"', '/', ':', '.', 'i', 'u', 's', 'c', 'v', 'f'
    );

    context.subscriptions.push(completionProvider);
}

function deactivate() {}

module.exports = {
    activate,
    deactivate
};