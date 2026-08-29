const vscode = require('vscode');

function activate(context) {
    // ---------------------------------------------------------
    // TARGET DEFINITIONS & METADATA
    // ---------------------------------------------------------
    const targets = {
        hecpp: { name: 'hecpp', desc: 'C++20 High Performance Native Binary (Clang/GCC)', category: 'native' },
        heasm: { name: 'heasm', desc: 'x86_64 Intel Assembly Source (.s) with LLVM Optimizations', category: 'native' },
        hejs: { name: 'hejs', desc: 'Node.js ES2022 JavaScript ESM Module', category: 'web' },
        hereact: { name: 'hereact', desc: 'React 19 Reactive UI Components & Hooks (.tsx)', category: 'ui' },
        hers: { name: 'hers', desc: 'Rust 2021 Safe Systems Conformance Target', category: 'native' },
        hepy: { name: 'hepy', desc: 'Python 3 Rapid Scripting & Reference Semantics', category: 'script' },
        hewasm: { name: 'hewasm', desc: 'WebAssembly (WASM/WAT) Binary Stack Engine', category: 'web' }
    };

    // ---------------------------------------------------------
    // 1. TARGET-AWARE CONTEXTUAL COMPLETION PROVIDER
    // ---------------------------------------------------------
    const completionProvider = vscode.languages.registerCompletionItemProvider(
        ['nyxlang', 'nyx', 'he', 'holyeasylang'],
        {
            provideCompletionItems(document, position, token, completionContext) {
                const items = [];
                const fullText = document.getText();

                // Detect in-file target
                let currentTarget = 'hecpp';
                const targetMatch = fullText.match(/^\s*#target\s+([a-zA-Z0-9_]+)/m);
                if (targetMatch) {
                    currentTarget = targetMatch[1].toLowerCase();
                }

                // Detect if #native or unsafe is present
                const hasNative = /#native\b/.test(fullText) || /unsafe\b/.test(fullText);

                function addSnippet(label, snippetText, detail, doc, kind = vscode.CompletionItemKind.Snippet) {
                    const item = new vscode.CompletionItem(label, kind);
                    item.insertText = new vscode.SnippetString(snippetText);
                    item.detail = detail;
                    item.documentation = new vscode.MarkdownString(doc);
                    items.push(item);
                }

                function addKw(label, detail, doc) {
                    const item = new vscode.CompletionItem(label, vscode.CompletionItemKind.Keyword);
                    item.detail = detail;
                    item.documentation = new vscode.MarkdownString(doc);
                    items.push(item);
                }

                // =====================================================
                // A. CORE LANGUAGE KEYWORDS & CONTROL FLOW (UNIVERSAL)
                // =====================================================
                addSnippet('fn', 'fn ${1:name}(${2:params}) -> ${3:type} {\n\t${0:// body}\n\treturn ${4:result};\n}', 'Function Definition', 'Declares a strongly-typed nyx function.');
                addSnippet('struct', 'struct ${1:Name} {\n\t${2:field}: ${3:type}\n}', 'Struct Definition', 'Declares a custom data structure.');
                addSnippet('impl', 'impl ${1:StructName} {\n\tfn ${2:method_name}(self${3:, params}) -> ${4:type} {\n\t\t${0:// method body}\n\t}\n}', 'Impl Block', 'Implements methods and traits for a struct.');
                addSnippet('var', 'var ${1:name} = ${2:value};', 'Mutable Variable', 'Declares a mutable variable with type inference.');
                addSnippet('const', 'const ${1:NAME} = ${2:value};', 'Constant', 'Declares an immutable compile-time constant.');
                addSnippet('if', 'if ${1:condition} {\n\t${0:// then body}\n}', 'If Condition', 'Branch execution.');
                addSnippet('ifelse', 'if ${1:condition} {\n\t${2:// true branch}\n} else {\n\t${0:// false branch}\n}', 'If-Else Condition', 'Two-way branch execution.');
                addSnippet('elif', 'elif ${1:condition} {\n\t${0:// branch}\n}', 'Elif Branch', 'Chained else-if branch.');
                addSnippet('for', 'for ${1:i} in ${2:0}..${3:count}-1 {\n\t${0:// loop body}\n}', 'For Range Loop', 'Iterates over a contiguous range.');
                addSnippet('for_in', 'for ${1:item} in ${2:collection} {\n\t${0:// process item}\n}', 'For-In Loop', 'Iterates over an array or collection.');
                addSnippet('while', 'while ${1:condition} {\n\t${0:// loop body}\n}', 'While Loop', 'Loops while condition is truthy.');
                addSnippet('match', 'match ${1:expr} {\n\t${2:pattern} => ${3:result},\n\t"_" => ${0:default}\n}', 'Pattern Matching', 'Pattern matching with exhaustiveness checks.');
                addSnippet('print', 'print(${1:expr});', 'Print to stdout', 'Prints expressions to the standard output console.');
                addSnippet('println', 'print(${1:expr});', 'Print line', 'Prints expressions to stdout.');
                addSnippet('import', 'import "${1:std/io}";', 'Import Module', 'Imports a standard library or local module.');
                addSnippet('test', 'test "${1:feature verification}" {\n\tassert(${2:condition}, "${3:failure message}");\n}', 'In-File Unit Test', 'Defines an automated unit test suite.');
                addSnippet('assert', 'assert(${1:condition}, "${2:message}");', 'Assertion', 'Asserts condition is true; halts with error if false.');
                addSnippet('try_catch', 'try {\n\t${1:// risky code}\n} catch (err) {\n\t${0:// handle error}\n}', 'Try-Catch', 'Exception handling block.');
                addSnippet('spawn', 'spawn {\n\t${0:// concurrent task}\n}', 'Spawn Thread', 'Spawns a background thread/task.');

                // Directives
                addSnippet('#target', '#target ${1|hecpp,heasm,hejs,hereact,hers,hepy,hewasm|}', 'Compiler Target Directive', 'Sets the active backend code generator for this source file.');
                addSnippet('#target hecpp', '#target hecpp\n\nfn main() {\n\tprint("Hello from nyx Native C++20!");\n}', 'C++20 Target Template', 'Initializes file for C++20 native compilation.');
                addSnippet('#target hereact', '#target hereact\n\nvar title = "nyx Reactive Web";\n\nfn main() {\n\tprint("Interactive Component Mounted");\n}', 'React Target Template', 'Initializes file for React 19 TSX UI component generation.');
                addSnippet('#target heasm', '#target heasm\n\nfn main() {\n\tprint("Direct x86_64 Intel Assembly");\n}', 'Assembly Target Template', 'Initializes file for Intel x86_64 assembly output.');

                // =====================================================
                // B. TARGET-SPECIFIC INTELLISENSE INJECTION
                // =====================================================

                // 1. REACT TARGET COMPLETIONS (#target hereact)
                if (currentTarget === 'hereact' || currentTarget === 'react') {
                    addSnippet('useState', 'var [${1:state}, set${1/(.*)/${1:/capitalize}/}] = useState(${2:initialValue});', 'React useState Hook', 'Declares state variable and updater function.', vscode.CompletionItemKind.Function);
                    addSnippet('useEffect', 'useEffect(() => {\n\t${0:// side effect}\n\treturn () => { ${1:// cleanup} };\n}, [${2:deps}]);', 'React useEffect Hook', 'Runs side effects on component lifecycle.', vscode.CompletionItemKind.Function);
                    addSnippet('useRef', 'var ${1:ref} = useRef(${2:null});', 'React useRef Hook', 'Creates a persistent mutable reference.', vscode.CompletionItemKind.Function);
                    addSnippet('useMemo', 'var ${1:memoized} = useMemo(() => ${2:compute}(), [${3:deps}]);', 'React useMemo Hook', 'Memoizes calculated values.', vscode.CompletionItemKind.Function);
                    addSnippet('useCallback', 'var ${1:callback} = useCallback((${2:params}) => {\n\t${0:// logic}\n}, [${3:deps}]);', 'React useCallback Hook', 'Memoizes callback functions.', vscode.CompletionItemKind.Function);
                    
                    // TSX / JSX UI Elements
                    addSnippet('div', '<div style={{ ${1:padding: 16} }}>\n\t$0\n</div>', 'JSX div Element', 'HTML container division.', vscode.CompletionItemKind.Property);
                    addSnippet('button', '<button onClick={() => ${1:handleClick}()} style={{ ${2:cursor: "pointer"} }}>\n\t${3:Click Me}\n</button>', 'JSX Button Element', 'Clickable interactive button.', vscode.CompletionItemKind.Property);
                    addSnippet('input', '<input type="${1|text,number,password,email|}" value={${2:state}} onChange={e => set${2/(.*)/${1:/capitalize}/}(e.target.value)} />', 'JSX Input Field', 'Controlled input field.', vscode.CompletionItemKind.Property);
                    addSnippet('card', '<div style={{ background: "#0c131d", border: "1px solid #1e293b", borderRadius: 8, padding: 20 }}>\n\t<h3>${1:Card Title}</h3>\n\t<p>${2:Content}</p>\n</div>', 'Cyberpunk UI Card', 'Pre-styled dark theme card container.', vscode.CompletionItemKind.Snippet);
                }

                // 2. NATIVE C++ / ASM / HARDWARE COMPLETIONS (#target hecpp / heasm / #native)
                if (currentTarget === 'hecpp' || currentTarget === 'heasm' || hasNative) {
                    addSnippet('#native include', '#native include <${1|iostream,vector,string,memory,algorithm,chrono,thread,cstdint,cmath,fstream,sstream|}>', 'Native C++ Header', 'Includes a C/C++ header in the generated translation unit.');
                    addSnippet('#native link', '#native link "${1|ws2_32,user32,gdi32,pthread,dl,m|}"', 'Link Library', 'Specifies a static or dynamic library to link with Clang/GCC.');
                    addSnippet('#native raw', '#native raw {\n\t${0:// raw C++20 code}\n}', 'Raw Native Block', 'Injects raw C++20 code directly into compilation.');
                    addSnippet('#native use', '#native use "${1|std,std::chrono,std::string_view|}";', 'Using Namespace Directive', 'Injects using namespace directive.');
                    addSnippet('extern_fn', 'extern fn ${1:name}(${2:params}) -> ${3:type};', 'C FFI Function Declaration', 'Declares an external C ABI function.');
                    
                    // Memory & Hardware APIs
                    addSnippet('unsafe_block', 'unsafe {\n\tvar ptr = addr(${1:variable});\n\tvar val = peek(ptr);\n\t${0}\n}', 'Unsafe Memory Block', 'Enables raw pointers and hardware dereferencing.');
                    addSnippet('addr', 'addr(${1:variable})', 'Get Raw Pointer Address', 'Returns uintptr memory address of variable (mov rax, rcx).', vscode.CompletionItemKind.Function);
                    addSnippet('peek', 'peek(${1:ptr})', 'Read Memory at Address', 'Dereferences 64-bit value at raw address (mov rax, [rcx]).', vscode.CompletionItemKind.Function);
                    addSnippet('poke', 'poke(${1:ptr}, ${2:value})', 'Write Memory at Address', 'Writes 64-bit value directly to raw memory address.', vscode.CompletionItemKind.Function);
                    addSnippet('memdump', 'memdump(${1:ptr}, ${2:num_bytes});', 'Hex Memory Dump', 'Dumps raw memory bytes formatted in hexadecimal to console.', vscode.CompletionItemKind.Function);
                    addSnippet('delay_ms', 'delay_ms(${1:1000});', 'High-Res Sleep (ms)', 'Pauses current thread with microsecond precision.', vscode.CompletionItemKind.Function);
                }

                // 3. NODE.JS / JAVASCRIPT COMPLETIONS (#target hejs)
                if (currentTarget === 'hejs' || currentTarget === 'js') {
                    addSnippet('fs_read', 'import "std/fs";\nvar content = fs_read_file("${1:path.txt}");', 'File Read (Node.js)', 'Reads file content asynchronously.', vscode.CompletionItemKind.Function);
                    addSnippet('fetch', 'var res = await fetch("${1:https://api.example.com/data}");\nvar json = await res.json();', 'HTTP Fetch', 'Performs network request.', vscode.CompletionItemKind.Function);
                    addSnippet('json_parse', 'var obj = JSON.parse(${1:json_string});', 'JSON Parse', 'Parses JSON string into object.', vscode.CompletionItemKind.Function);
                }

                // =====================================================
                // C. IDENTIFIERS & SYMBOLS DISCOVERY
                // =====================================================
                const symRegex = /\b(?:var|let|const|fn|struct|enum|trait)\s+([a-zA-Z_][a-zA-Z0-9_]*)/g;
                let match;
                const seen = new Set();
                while ((match = symRegex.exec(fullText)) !== null) {
                    const sym = match[1];
                    if (!seen.has(sym)) {
                        seen.add(sym);
                        const symItem = new vscode.CompletionItem(sym, vscode.CompletionItemKind.Variable);
                        symItem.detail = `Local Symbol: ${sym}`;
                        items.push(symItem);
                    }
                }

                return items;
            }
        },
        '#', '.', ' ', '<', ':', '"' // Triggers
    );

    // ---------------------------------------------------------
    // 2. RICH HOVER DOCUMENTATION PROVIDER
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
                'assert': '**`assert(condition: bool, message: string)`**\n\nVerifies condition invariant at runtime; exits with error message on failure.',
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