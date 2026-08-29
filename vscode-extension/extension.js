const vscode = require('vscode');

function activate(context) {
    // ---------------------------------------------------------
    // STANDARD MODULES & C++ HEADERS REPOSITORY
    // ---------------------------------------------------------
    const stdModules = [
        { name: 'std/io', desc: 'Console standard input/output streams and formatting' },
        { name: 'std/fs', desc: 'File system operations (read, write, exists, remove)' },
        { name: 'std/math', desc: 'Mathematical constants and functions (pow, sqrt, sin, cos, PI)' },
        { name: 'std/time', desc: 'High-resolution timers, timestamps, and delay_ms()' },
        { name: 'std/memory', desc: 'Low-level hardware pointers, addr(), peek(), poke(), memdump()' },
        { name: 'std/os', desc: 'Operating system interop, platform info, env variables' },
        { name: 'std/net', desc: 'TCP/IP sockets and networking streams' },
        { name: 'std/gpio', desc: 'Embedded microcontroller GPIO pin input/output control' },
        { name: 'std/serial', desc: 'UART/USART serial communication port API' },
        { name: 'std/spi', desc: 'SPI bus hardware communication' },
        { name: 'std/i2c', desc: 'I2C two-wire hardware interface' },
        { name: 'std/process', desc: 'Child process execution and pipeline management' },
        { name: 'std/str', desc: 'Advanced string manipulation and Unicode helpers' },
        { name: 'std/platform', desc: 'Cross-platform hardware architecture detection' },
        { name: 'std/env', desc: 'Environment configuration access' }
    ];

    const cppHeaders = [
        'iostream', 'vector', 'string', 'memory', 'algorithm', 'chrono', 'thread',
        'cstdint', 'cmath', 'fstream', 'sstream', 'map', 'set', 'unordered_map',
        'unordered_set', 'functional', 'utility', 'tuple', 'variant', 'optional',
        'span', 'format', 'ranges', 'concepts', 'windows.h', 'unistd.h', 'sys/socket.h'
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
    // 1. CONTEXTUAL INTELLISENSE & CONTINUOUS AUTOCOMPLETE
    // ---------------------------------------------------------
    const completionProvider = vscode.languages.registerCompletionItemProvider(
        ['nyxlang', 'nyx', 'he', 'holyeasylang'],
        {
            provideCompletionItems(document, position, token, completionContext) {
                const items = [];
                const lineText = document.lineAt(position).text;
                const linePrefix = lineText.substring(0, position.character);
                const fullText = document.getText();

                // Detect in-file target
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

                function addSimpleItem(label, insertText, detail, kind = vscode.CompletionItemKind.Value) {
                    const item = new vscode.CompletionItem(label, kind);
                    item.insertText = insertText;
                    item.detail = detail;
                    items.push(item);
                }

                // =====================================================
                // CASE 1: Typing after "#native "
                // =====================================================
                if (/#native\s*$/i.test(linePrefix)) {
                    addSnippet('include', 'include <${1|iostream,vector,string,memory,chrono,thread,cstdint,cmath,fstream|}>', '#native include <header>', 'Includes native C/C++ header.');
                    addSnippet('link', 'link "${1|ws2_32,user32,gdi32,pthread,dl,m|}"', '#native link "library"', 'Links external system library with linker.');
                    addSnippet('raw', 'raw {\n\t${0:// raw C++20 code}\n}', '#native raw { ... }', 'Direct inline C++ code injection block.');
                    addSnippet('use', 'use "${1|namespace std,std::chrono,std::string_view|}";', '#native use "namespace"', 'Injects C++ using namespace declaration.');
                    return items;
                }

                // =====================================================
                // CASE 2: Typing after "#native include" or "<"
                // =====================================================
                if (/#native\s+include\s*<?$/i.test(linePrefix) || (/#native\s+include\s+/i.test(linePrefix) && linePrefix.endsWith('<'))) {
                    cppHeaders.forEach(h => {
                        const item = new vscode.CompletionItem(h, vscode.CompletionItemKind.Module);
                        item.insertText = `<${h}>`;
                        item.detail = `C++ Header: <${h}>`;
                        item.documentation = new vscode.MarkdownString(`Standard C/C++ library header \`<${h}>\``);
                        items.push(item);
                    });
                    return items;
                }

                // =====================================================
                // CASE 3: Typing after "#target "
                // =====================================================
                if (/#target\s*$/i.test(linePrefix)) {
                    targetsList.forEach(t => {
                        const item = new vscode.CompletionItem(t.name, vscode.CompletionItemKind.EnumMember);
                        item.insertText = t.name;
                        item.detail = `Target: ${t.desc}`;
                        items.push(item);
                    });
                    return items;
                }

                // =====================================================
                // CASE 4: Typing after "import " or "use "
                // =====================================================
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

                // =====================================================
                // CASE 5: General Top-Level Directives (Typing "#")
                // =====================================================
                addSnippet('#target', '#target ${1|hecpp,heasm,hereact,hejs,hers,hepy,hewasm|}', 'Target Directive', 'Sets compilation backend target.');
                addSnippet('#native include', '#native include <${1|iostream,vector,string,memory,chrono,thread,cstdint,cmath,fstream|}>', 'Native Include', 'Includes C/C++ header directly.');
                addSnippet('#native link', '#native link "${1|ws2_32,user32,gdi32,pthread,dl,m|}"', 'Native Link', 'Links system library.');
                addSnippet('#native raw', '#native raw {\n\t${0:// raw C++20 code}\n}', 'Native Raw Block', 'Injects raw C++ code.');
                addSnippet('#native use', '#native use "${1|namespace std,std::chrono,std::string_view|}";', 'Native Use Directive', 'Namespace injection.');

                // =====================================================
                // CASE 6: Core Language Features
                // =====================================================
                addSnippet('fn', 'fn ${1:name}(${2:params}) -> ${3:type} {\n\t${0:// body}\n\treturn ${4:result};\n}', 'Function Definition', 'Declares a strongly-typed function.');
                addSnippet('struct', 'struct ${1:Name} {\n\t${2:field}: ${3:type}\n}', 'Struct Definition', 'Declares a custom data structure.');
                addSnippet('impl', 'impl ${1:StructName} {\n\tfn ${2:method_name}(self${3:, params}) -> ${4:type} {\n\t\t${0:// method body}\n\t}\n}', 'Impl Block', 'Implements methods for a struct.');
                addSnippet('var', 'var ${1:name} = ${2:value};', 'Mutable Variable', 'Declares a mutable variable.');
                addSnippet('const', 'const ${1:NAME} = ${2:value};', 'Constant', 'Declares an immutable constant.');
                addSnippet('if', 'if ${1:condition} {\n\t${0:// then branch}\n}', 'If Block', 'Conditional branch.');
                addSnippet('ifelse', 'if ${1:condition} {\n\t${2:// true branch}\n} else {\n\t${0:// false branch}\n}', 'If-Else Block', 'Two-way conditional branch.');
                addSnippet('for', 'for ${1:i} in ${2:0}..${3:count}-1 {\n\t${0:// loop body}\n}', 'For Range Loop', 'Iterates over a contiguous range.');
                addSnippet('while', 'while ${1:condition} {\n\t${0:// loop body}\n}', 'While Loop', 'Iterates while condition is true.');
                addSnippet('match', 'match ${1:expr} {\n\t${2:pattern} => ${3:result},\n\t"_" => ${0:default}\n}', 'Pattern Matching', 'Pattern matching block.');
                addSnippet('print', 'print(${1:expr});', 'Print to Console', 'Prints expressions to stdout.');
                addSnippet('import', 'import "${1:std/io}";', 'Import Module', 'Imports standard library or local module.');
                addSnippet('test', 'test "${1:test title}" {\n\tassert(${2:condition}, "${3:failure message}");\n}', 'Unit Test Block', 'Defines an automated in-file unit test.');
                addSnippet('assert', 'assert(${1:condition}, "${2:message}");', 'Assertion', 'Asserts condition is true; halts on failure.');

                // =====================================================
                // CASE 7: Target-Specific Features
                // =====================================================
                if (currentTarget === 'hereact' || currentTarget === 'react') {
                    addSnippet('useState', 'var [${1:state}, set${1/(.*)/${1:/capitalize}/}] = useState(${2:initialValue});', 'React useState Hook', 'Reactive state variable with updater.', vscode.CompletionItemKind.Function);
                    addSnippet('useEffect', 'useEffect(() => {\n\t${0:// side effect}\n}, [${1:deps}]);', 'React useEffect Hook', 'Component lifecycle side-effect hook.', vscode.CompletionItemKind.Function);
                    addSnippet('useRef', 'var ${1:ref} = useRef(${2:null});', 'React useRef Hook', 'Persistent mutable reference.', vscode.CompletionItemKind.Function);
                    addSnippet('card', '<div style={{ background: "#0c131d", border: "1px solid #1e293b", borderRadius: 8, padding: 20 }}>\n\t<h3>${1:Title}</h3>\n\t<p>${2:Content}</p>\n</div>', 'Cyberpunk UI Card', 'Pre-styled dark theme card container.', vscode.CompletionItemKind.Snippet);
                }

                if (currentTarget === 'hecpp' || currentTarget === 'heasm' || hasNative) {
                    addSnippet('unsafe', 'unsafe {\n\tvar ptr = addr(${1:variable});\n\tvar val = peek(ptr);\n\t${0}\n}', 'Unsafe Memory Block', 'Permits direct pointer arithmetic and dereferencing.');
                    addSnippet('addr', 'addr(${1:variable})', 'Get Pointer Address', 'Returns 64-bit physical memory address of variable.', vscode.CompletionItemKind.Function);
                    addSnippet('peek', 'peek(${1:ptr})', 'Read Memory Address', 'Dereferences 64-bit value at raw address.', vscode.CompletionItemKind.Function);
                    addSnippet('poke', 'poke(${1:ptr}, ${2:value})', 'Write Memory Address', 'Writes 64-bit value directly to memory address.', vscode.CompletionItemKind.Function);
                    addSnippet('memdump', 'memdump(${1:ptr}, ${2:num_bytes});', 'Hex Memory Dump', 'Dumps raw memory bytes formatted in hexadecimal.', vscode.CompletionItemKind.Function);
                    addSnippet('delay_ms', 'delay_ms(${1:1000});', 'High-Res Sleep', 'Thread sleep with microsecond precision.', vscode.CompletionItemKind.Function);
                }

                // Scope identifiers
                const symRegex = /\b(?:var|let|const|fn|struct|enum)\s+([a-zA-Z_][a-zA-Z0-9_]*)/g;
                let match;
                const seen = new Set();
                while ((match = symRegex.exec(fullText)) !== null) {
                    const sym = match[1];
                    if (!seen.has(sym)) {
                        seen.add(sym);
                        const symItem = new vscode.CompletionItem(sym, vscode.CompletionItemKind.Variable);
                        symItem.detail = `Symbol: ${sym}`;
                        items.push(symItem);
                    }
                }

                return items;
            }
        },
        '#', ' ', '<', '"', '/', ':', '.' // Trigger characters for continuous autocomplete
    );

    // ---------------------------------------------------------
    // 2. HOVER DOCUMENTATION PROVIDER
    // ---------------------------------------------------------
    const hoverProvider = vscode.languages.registerHoverProvider(['nyxlang', 'nyx', 'he', 'holyeasylang'], {
        provideHover(document, position, token) {
            const range = document.getWordRangeAtPosition(position, /#?[a-zA-Z_0-9]+/);
            if (!range) return null;
            const word = document.getText(range);

            const hoverDocs = {
                '#target': '**`#target <backend>`**\n\nSets the active compilation backend target for this file.\n\n*Supported targets:*\n- `hecpp` (C++20 Native Executable)\n- `heasm` (x86_64 Intel Assembly)\n- `hereact` (React 19 TSX UI Component)\n- `hejs` (Node.js ES2022 Module)\n- `hers` (Rust 2021 Conformance)\n- `hepy` (Python 3 Reference)\n- `hewasm` (WebAssembly Stack Engine)',
                '#native': '**`#native <include|link|raw|use>`**\n\nEscape hatch for zero-overhead C/C++ hardware interop.\n\n```nyx\n#native include <iostream>\n#native link "ws2_32"\n#native raw { std::cout << "Direct C++"; }\n```',
                'addr': '**`addr(variable: T) -> uintptr`**\n\nReturns the 64-bit physical memory address of a variable.\n\n*Hardware Assembly:* `mov rax, rcx` (Zero Overhead)',
                'peek': '**`peek(ptr: uintptr) -> int`**\n\nSafely or unsafely dereferences memory at a raw 64-bit pointer address.\n\n*Hardware Assembly:* `mov rax, [rcx]`',
                'poke': '**`poke(ptr: uintptr, value: int)`**\n\nWrites a 64-bit value directly to a memory address.',
                'memdump': '**`memdump(ptr: uintptr, bytes: int)`**\n\nOutputs a formatted hexadecimal memory dump to console.',
                'delay_ms': '**`delay_ms(milliseconds: int)`**\n\nPauses current execution thread with high-precision sleep.',
                'fn': '**`fn name(params) -> ReturnType`**\n\nDefines a strongly typed nyx function.',
                'struct': '**`struct Name { field: Type }`**\n\nDefines a custom data layout with zero padding overhead.',
                'impl': '**`impl StructName { ... }`**\n\nEncapsulates member methods, constructors, and RAII destructors.',
                'unsafe': '**`unsafe { ... }`**\n\nDeclares an unsafe memory boundary where raw pointer arithmetic and dereferencing are permitted.',
                'test': '**`test "description" { ... }`**\n\nDefines an automated unit test evaluated during `nyx test`.',
                'assert': '**`assert(condition: bool, message: string)`**\n\nVerifies condition invariant at runtime; halts with error message on failure.',
                'useState': '**`useState<T>(initialValue: T) -> [T, (val: T) => void]`** *(React 19)*\n\nDeclares component state and reactive updater function.',
                'useEffect': '**`useEffect(effectFn, depsArray)`** *(React 19)*\n\nExecutes side-effects on component mount, update, or unmount.'
            };

            if (hoverDocs[word]) {
                return new vscode.Hover(new vscode.MarkdownString(hoverDocs[word]));
            }
            return null;
        }
    });

    context.subscriptions.push(completionProvider, hoverProvider);
}

function deactivate() {}

module.exports = {
    activate,
    deactivate
};