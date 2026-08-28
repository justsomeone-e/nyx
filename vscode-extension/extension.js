const vscode = require('vscode');

function activate(context) {
    const targetsList = [
        { name: 'hecpp', desc: 'C++20 High Performance Native Binary' },
        { name: 'hereact', desc: 'React (TSX / JSX) Modern Web UI' },
        { name: 'react', desc: 'React (TSX / JSX) Modern Web UI' },
        { name: 'hec', desc: 'ANSI C Pure Low-Level Engine' },
        { name: 'hejs', desc: 'JavaScript / Web / Node.js Engine' },
        { name: 'hepy', desc: 'Python 3 Rapid Scripting & ML' },
        { name: 'hego', desc: 'Go / Golang Concurrency & Backend' },
        { name: 'herust', desc: 'Rust Memory-Safe Native Target' },
        { name: 'hejava', desc: 'Java JVM Cross-Platform App' },
        { name: 'hecs', desc: 'C# / .NET Game & Enterprise App' },
        { name: 'heino', desc: 'Arduino / ESP32 Hardware Firmware' },
        { name: 'heasm', desc: 'X86_64 Pure Assembly Code' }
    ];

    const provider = vscode.languages.registerCompletionItemProvider('holyeasylang', {
        provideCompletionItems(document, position, token, completionContext) {
            const items = [];

            function addSnippet(label, snippetText, detail, doc) {
                const item = new vscode.CompletionItem(label, vscode.CompletionItemKind.Snippet);
                item.insertText = new vscode.SnippetString(snippetText);
                item.detail = detail;
                item.documentation = new vscode.MarkdownString(doc);
                items.push(item);
            }

            function addKeyword(label, detail, doc) {
                const item = new vscode.CompletionItem(label, vscode.CompletionItemKind.Keyword);
                item.detail = detail;
                item.documentation = new vscode.MarkdownString(doc);
                items.push(item);
            }

            // 1. DIRECTIVES & TARGETS
            addSnippet('#target', '#target ${1|hecpp,hereact,hejs,hepy,hec,hego,herust,hejava,hecs,heino,heasm|} // Note: Only 1 #target allowed per file', 'target directive', 'Specifies HolyEasyLang compilation target.');
            addSnippet('target', '#target ${1|hecpp,hereact,hejs,hepy,hec,hego,herust,hejava,hecs,heino,heasm|} // Note: Only 1 #target allowed per file', 'target directive', 'Specifies HolyEasyLang compilation target.');
            addSnippet('#native', '#native ${1|hecpp,hepy,hereact,hejs|}: ${2:#include <windows.h>}', '#native escape hatch', 'Injects raw native target library code directly.');
            addSnippet('native', '#native ${1|hecpp,hepy,hereact,hejs|}: ${2:#include <windows.h>}', '#native escape hatch', 'Injects raw native target library code directly.');

            targetsList.forEach(t => {
                const item = new vscode.CompletionItem(t.name, vscode.CompletionItemKind.EnumMember);
                item.detail = `Target: ${t.desc}`;
                items.push(item);
            });

            // 2. PIPELINE & FLOW OPERATORS
            addSnippet('pipe', '${1:value} |> ${2:func} |> print', 'pipeline operator (|>)', 'Passes the left expression output into the right function as argument.');
            addSnippet('arrow', '${1:value} -> ${2:variable_name}', 'arrow assignment (->)', 'Assigns the left value to the right variable.');

            // 3. CONTROL FLOW SNIPPETS
            addSnippet('continue', 'continue', 'continue statement', 'Skips the remaining statements in current iteration.');
            addSnippet('break', 'break', 'break statement', 'Breaks out of current loop.');
            addSnippet('if', 'if ${1:condition}:\n\t${0:// body}', 'if statement', 'Conditional execution block.');
            addSnippet('ifel', 'if ${1:condition}:\n\t${2:// true block}\nelse:\n\t${0:// false block}', 'if-else statement', 'If-else conditional branching.');
            addSnippet('ifelif', 'if ${1:condition1}:\n\t${2:// block 1}\nelif ${3:condition2}:\n\t${4:// block 2}\nelse:\n\t${0:// block 3}', 'if-elif-else statement', 'Multi-conditional branching.');
            addSnippet('fn', 'fn ${1:name}(${2:params}):\n\t${0:// body}\n\treturn ${3:result}', 'fn (function definition)', 'Declares a reusable function.');
            addSnippet('for', 'for ${1:i} in ${2:1}..${3:10}:\n\t${0:print($1)}', 'for range loop', 'Iterates over a numerical range.');
            addSnippet('loop', 'loop ${1:condition}:\n\t${0:// loop body}', 'loop statement', 'Repeats execution while condition is true.');
            addSnippet('var', 'var ${1:name} = ${2:value}', 'var variable declaration', 'Declares a new variable.');
            addSnippet('let', 'let ${1:name} = ${2:value}', 'let variable declaration', 'Declares a modern variable.');
            addSnippet('const', 'const ${1:NAME} = ${2:value}', 'const constant declaration', 'Declares an immutable constant.');
            addSnippet('print', 'print(${1:"message"})', 'print statement', 'Prints values to standard output.');
            addSnippet('use', 'use "${1:./module.he}"', 'use file module', 'Imports and links a local .he module file.');

            // Memory Snippets
            addSnippet('addr', 'addr(${1:variable})', 'addr(variable) : uintptr_t', 'Gets physical 64-bit RAM memory address.');
            addSnippet('peek', 'peek(${1:address})', 'peek(address) : uint64_t', 'Reads raw value from memory address.');
            addSnippet('memdump', 'memdump(${1:address}, ${2:16})', 'memdump(address, length)', 'Dumps memory in Hex and ASCII table.');

            // 4. KEYWORDS
            const kws = ['continue', 'break', 'if', 'else', 'elif', 'fn', 'return', 'for', 'in', 'loop', 'var', 'let', 'set', 'const', 'use'];
            kws.forEach(kw => addKeyword(kw, `keyword ${kw}`, `HolyEasyLang keyword \`${kw}\``));

            // 5. USER VARIABLES
            const text = document.getText();
            const varRegex = /\b(?:var|let|set|const)\s+([a-zA-Z_][a-zA-Z0-9_]*)/g;
            let match;
            const seen = new Set();
            while ((match = varRegex.exec(text)) !== null) {
                const varName = match[1];
                if (!seen.has(varName)) {
                    seen.add(varName);
                    const varItem = new vscode.CompletionItem(varName, vscode.CompletionItemKind.Variable);
                    varItem.detail = `Variable: ${varName}`;
                    items.push(varItem);
                }
            }

            return items;
        }
    });

    context.subscriptions.push(provider);
}

function deactivate() {}

module.exports = {
    activate,
    deactivate
};
