const vscode = require('vscode');

function activate(context) {
    const targetsList = [
        { name: 'hecpp', desc: 'C++20 High Performance Native Binary' },
        { name: 'hejs', desc: 'JavaScript / Web / Node.js Engine (ES2022)' },
        { name: 'hers', desc: 'Rust 2021 Memory-Safe Conformance Target' },
        { name: 'hepy', desc: 'Python 3 Rapid Scripting & ML Reference' },
        { name: 'hereact', desc: 'React (TSX / JSX) Modern Web UI' },
        { name: 'heasm', desc: 'x86_64 Pure Assembly Code' }
    ];

    const provider = vscode.languages.registerCompletionItemProvider(['nyxlang', 'nyx', 'he', 'holyeasylang'], {
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
            addSnippet('#target', '#target ${1|hecpp,hejs,hers,hepy,hereact,heasm|}', 'target directive', 'Specifies nyx compilation backend target.');
            addSnippet('target', '#target ${1|hecpp,hejs,hers,hepy,hereact,heasm|}', 'target directive', 'Specifies nyx compilation backend target.');
            addSnippet('#native', '#native ${1|hecpp,hepy,hejs,hers|}: ${2:#include <iostream>}', '#native escape hatch', 'Injects raw native target library code directly.');

            targetsList.forEach(t => {
                const item = new vscode.CompletionItem(t.name, vscode.CompletionItemKind.EnumMember);
                item.detail = `Target: ${t.desc}`;
                items.push(item);
            });

            // 2. OPERATORS
            addSnippet('pipe', '${1:value} |> ${2:func}', 'pipeline operator (|>)', 'Passes the left expression output into the right function as argument.');
            addSnippet('arrow', '${1:value} -> ${2:variable_name}', 'arrow assignment (->)', 'Assigns the left value to the right variable.');

            // 3. CONTROL FLOW SNIPPETS & KEYWORDS
            addSnippet('continue', 'continue', 'continue statement', 'Skips to the next iteration of the current loop.');
            addSnippet('break', 'break', 'break statement', 'Terminates and exits the current loop.');
            addSnippet('return', 'return ${1:value}', 'return statement', 'Returns a value from the current function.');
            addSnippet('if', 'if ${1:condition} {\n\t${0:// body}\n}', 'if block', 'Conditional branch execution.');
            addSnippet('ifelse', 'if ${1:condition} {\n\t${2:// true block}\n} else {\n\t${0:// false block}\n}', 'if-else block', 'Conditional if-else branching.');
            addSnippet('elif', 'elif ${1:condition} {\n\t${0:// branch}\n}', 'elif branch', 'Else-if condition.');
            addSnippet('for', 'for ${1:i} in ${2:1}..${3:10} {\n\t${0:print($1)}\n}', 'for range loop', 'Iterates over a range or collection.');
            addSnippet('while', 'while ${1:condition} {\n\t${0:// loop body}\n}', 'while loop', 'Repeats execution while condition is true.');
            addSnippet('loop', 'loop {\n\t${0:// infinite loop}\n\tif ${1:condition} { break }\n}', 'loop statement', 'Unconditional loop.');
            addSnippet('match', 'match ${1:expr} {\n\t${2:pattern} => ${3:result},\n\t"_" => ${0:default}\n}', 'match pattern matching', 'Pattern matching expression.');
            addSnippet('fn', 'fn ${1:name}(${2:params}) -> ${3:type} {\n\t${0:// body}\n\treturn ${4:result}\n}', 'fn declaration', 'Declares a strongly typed function.');
            addSnippet('struct', 'struct ${1:Name} {\n\t${2:field1}: ${3:type},\n\t${4:field2}: ${5:type}\n}', 'struct definition', 'Declares a custom data structure.');
            addSnippet('var', 'var ${1:name} = ${2:value}', 'var declaration', 'Declares a variable.');
            addSnippet('let', 'let ${1:name} = ${2:value}', 'let declaration', 'Declares a variable.');
            addSnippet('const', 'const ${1:NAME} = ${2:value}', 'const declaration', 'Declares an immutable constant.');
            addSnippet('print', 'print(${1:"message"})', 'print statement', 'Prints values to standard output.');
            addSnippet('import', 'import "${1:./module.nyx}"', 'import module', 'Imports and links a local .nyx module file.');
            addSnippet('import_selective', 'import { ${1:symbol} } from "${2:./module.nyx}"', 'selective import', 'Selectively imports symbols from a module.');
            addSnippet('test', 'test "${1:test name}" {\n\tassert(${2:condition}, "${3:message}")\n}', 'test block', 'Defines an in-file unit test.');
            addSnippet('unsafe', 'unsafe {\n\t${0:// raw memory operations}\n}', 'unsafe block', 'Allows direct memory operations (addr, peek, memdump).');

            // 4. KEYWORDS
            const kws = [
                'continue', 'break', 'return', 'if', 'else', 'elif', 'for', 'in', 'while', 'loop',
                'match', 'fn', 'struct', 'var', 'let', 'const', 'import', 'export', 'unsafe',
                'test', 'assert', 'true', 'false', 'null', 'Ok', 'Err', 'try', 'catch', 'type'
            ];
            kws.forEach(kw => addKeyword(kw, `keyword ${kw}`, `nyx keyword \`${kw}\``));

            // 5. LOCAL SCOPE VARIABLES
            const text = document.getText();
            const varRegex = /\b(?:var|let|const|fn|struct)\s+([a-zA-Z_][a-zA-Z0-9_]*)/g;
            let match;
            const seen = new Set();
            while ((match = varRegex.exec(text)) !== null) {
                const symName = match[1];
                if (!seen.has(symName)) {
                    seen.add(symName);
                    const varItem = new vscode.CompletionItem(symName, vscode.CompletionItemKind.Variable);
                    varItem.detail = `Symbol: ${symName}`;
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
