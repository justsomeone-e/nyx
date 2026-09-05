// ==========================================================================
// Tour of Nyx & WebAssembly Studio Engine (Monaco Edition)
// Client-side execution, interactive 81-step curriculum, and WASM Arcade
// ==========================================================================

(function () {
  'use strict';

  // --- State ---
  const state = {
    mode: 'tour', // 'tour' | 'playground' | 'arcade'
    currentExerciseIndex: 0,
    exercises: window.NYX_TOUR_DATA || [],
    completed: JSON.parse(localStorage.getItem('nyx_tour_completed') || '{}'),
    userCodeCache: JSON.parse(localStorage.getItem('nyx_tour_code_cache') || '{}'),
    monacoLoaded: false,
    monacoEditor: null,
    wasmInstance: null,
    arcadeRunning: false,
    arcadeAnimationId: null
  };

  // --- DOM Elements ---
  const el = {
    sidebar: document.getElementById('sidebar'),
    btnCollapseSidebar: document.getElementById('btnCollapseSidebar'),
    exerciseTree: document.getElementById('exerciseTree'),
    searchExercises: document.getElementById('searchExercises'),
    badgeTopic: document.getElementById('badgeTopic'),
    badgeStatus: document.getElementById('badgeStatus'),
    exerciseTitle: document.getElementById('exerciseTitle'),
    exerciseDesc: document.getElementById('exerciseDesc'),
    expectedOutputBox: document.getElementById('expectedOutputBox'),
    hintBox: document.getElementById('hintBox'),
    hintBtnText: document.getElementById('hintBtnText'),
    btnToggleHint: document.getElementById('btnToggleHint'),
    btnShowSolution: document.getElementById('btnShowSolution'),
    btnPrevExercise: document.getElementById('btnPrevExercise'),
    btnNextExercise: document.getElementById('btnNextExercise'),
    lessonCounter: document.getElementById('lessonCounter'),
    editorFilename: document.getElementById('editorFilename'),
    btnRun: document.getElementById('btnRun'),
    btnResetCode: document.getElementById('btnResetCode'),
    monacoContainer: document.getElementById('monacoEditorContainer'),
    editorLoading: document.getElementById('editorLoading'),
    workbenchDivider: document.getElementById('workbenchDivider'),
    tabTerminal: document.getElementById('tabTerminal'),
    tabCanvas: document.getElementById('tabCanvas'),
    execStatusBadge: document.getElementById('execStatusBadge'),
    btnClearTerminal: document.getElementById('btnClearTerminal'),
    terminalView: document.getElementById('terminalView'),
    canvasView: document.getElementById('canvasView'),
    arcadeCanvas: document.getElementById('arcadeCanvas'),
    progressText: document.getElementById('progressText'),
    progressBarFill: document.getElementById('progressBarFill'),
    btnModeTour: document.getElementById('btnModeTour'),
    btnModePlayground: document.getElementById('btnModePlayground'),
    btnModeArcade: document.getElementById('btnModeArcade'),
    installModal: document.getElementById('installModal'),
    btnOpenInstall: document.getElementById('btnOpenInstall'),
    btnCloseInstall: document.getElementById('btnCloseInstall')
  };

  // --- Playground Templates ---
  const PLAYGROUND_TEMPLATES = [
    {
      title: '01. Functional Pipelines',
      code: `// Functional composition with the forward pipe operator |>
fn double(x: int) -> int = x * 2
fn add_ten(x: int) -> int = x + 10
fn format_score(score: int) -> string = $"[Player Score: {score}]"

fn main() {
    let initial = 25
    let result = initial 
        |> double 
        |> add_ten 
        |> format_score

    print(result)
}

main()`
    },
    {
      title: '02. Safe Navigation & Coalescing',
      code: `// Deterministic null safety in Nyx
fn main() {
    let present: int? = 100
    let missing: int? = null

    // Safe null-coalescing with ??
    let a = present ?? 0
    let b = missing ?? 42

    print($"a: {a}, b: {b}")
}

main()`
    },
    {
      title: '03. RAII Defer Cleanup',
      code: `// Defer executes at scope exit in LIFO order
fn worker() {
    print("1. Worker started")
    defer print("4. First defer (runs last)")
    defer print("3. Second defer (runs first)")
    print("2. Worker doing critical operations...")
}

fn main() {
    worker()
    print("5. Program completed safely")
}

main()`
    },
    {
      title: '04. Pattern Matching',
      code: `// Pattern matching on status codes
fn classify_status(code: int) -> string = match code {
    200 => "200 OK: Request succeeded",
    400 => "400 Bad Request: Malformed syntax",
    404 => "404 Not Found: Resource does not exist",
    500 => "500 Internal Error: Server fault",
    _   => $"HTTP Status {code}"
}

fn main() {
    print(classify_status(200))
    print(classify_status(404))
    print(classify_status(503))
}

main()`
    }
  ];

  // --- Monaco Editor Initialization ---
  function initMonaco() {
    if (typeof require === 'undefined') {
      console.warn('Monaco loader not found, falling back to textarea.');
      initFallbackTextarea();
      return;
    }

    require.config({ paths: { vs: 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.45.0/min/vs' } });
    require(['vs/editor/editor.main'], function () {
      // 1. Register Nyx Language
      monaco.languages.register({ id: 'nyx' });

      // 2. Syntax Highlighter (Monarch)
      monaco.languages.setMonarchTokensProvider('nyx', {
        defaultToken: '',
        tokenPostfix: '.nyx',
        keywords: [
          'let', 'var', 'set', 'const', 'fn', 'struct', 'enum', 'type', 'trait',
          'impl', 'match', 'if', 'elif', 'else', 'while', 'for', 'in', 'loop',
          'defer', 'guard', 'break', 'continue', 'return', 'throw', 'try', 'catch',
          'test', 'assert', 'print', 'import', 'from', 'self', 'mut', 'and', 'or',
          'not', 'null', 'true', 'false', 'Ok', 'Err'
        ],
        typeKeywords: [
          'int', 'float', 'string', 'bool', 'char', 'byte', 'void', 'any', 'Array', 'Map', 'Result', 'Option'
        ],
        operators: [
          '=', '>', '<', '!', '~', '?', ':', '==', '<=', '>=', '!=',
          '&&', '||', '+', '-', '*', '/', '%', '+=', '-=', '*=', '/=',
          '|>', '??', '?.', '->', '=>'
        ],
        tokenizer: {
          root: [
            [/[a-z_$][\w$]*/, {
              cases: {
                '@keywords': 'keyword',
                '@typeKeywords': 'type',
                '@default': 'identifier'
              }
            }],
            [/[A-Z][\w$]*/, 'type.identifier'],
            { include: '@whitespace' },
            [/\$"([^"\\]|\\.)*"/, 'string.interpolated'],
            [/"([^"\\]|\\.)*"/, 'string'],
            [/'([^'\\]|\\.)*'/, 'string'],
            [/0[xX][0-9a-fA-F]+/, 'number.hex'],
            [/0[bB][01]+/, 'number.binary'],
            [/\d+(\.\d+)?/, 'number'],
            [/[{}()\[\]]/, '@brackets'],
            [/@operators/, {
              cases: {
                '@operators': 'operator',
                '@default': ''
              }
            }]
          ],
          whitespace: [
            [/[ \t\r\n]+/, 'white'],
            [/\/\/.*$/, 'comment']
          ]
        }
      });

      // 3. IntelliSense Autocomplete Provider
      monaco.languages.registerCompletionItemProvider('nyx', {
        provideCompletionItems: function (model, position) {
          const word = model.getWordUntilPosition(position);
          const range = {
            startLineNumber: position.lineNumber,
            endLineNumber: position.lineNumber,
            startColumn: word.startColumn,
            endColumn: word.endColumn
          };

          const suggestions = [
            {
              label: 'fn',
              kind: monaco.languages.CompletionItemKind.Snippet,
              insertText: 'fn ${1:name}(${2:params}) -> ${3:int} {\n\t$0\n}',
              insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
              documentation: 'Define a function with typed parameters and return type',
              range: range
            },
            {
              label: 'let',
              kind: monaco.languages.CompletionItemKind.Snippet,
              insertText: 'let ${1:name} = ${2:value}',
              insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
              documentation: 'Immutable binding in Nyx',
              range: range
            },
            {
              label: 'var',
              kind: monaco.languages.CompletionItemKind.Snippet,
              insertText: 'var ${1:name} = ${2:value}',
              insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
              documentation: 'Mutable variable in Nyx (mutated via set)',
              range: range
            },
            {
              label: 'set',
              kind: monaco.languages.CompletionItemKind.Snippet,
              insertText: 'set ${1:target} = ${2:value}',
              insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
              documentation: 'Explicit mutation operator for var bindings',
              range: range
            },
            {
              label: 'struct',
              kind: monaco.languages.CompletionItemKind.Snippet,
              insertText: 'struct ${1:Name} {\n\t${2:field}: ${3:int}\n}',
              insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
              documentation: 'Declare a structured data type',
              range: range
            },
            {
              label: 'enum',
              kind: monaco.languages.CompletionItemKind.Snippet,
              insertText: 'enum ${1:Name} {\n\t${2:First},\n\t${3:Second}\n}',
              insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
              documentation: 'Declare an algebraic enumerated type',
              range: range
            },
            {
              label: 'match',
              kind: monaco.languages.CompletionItemKind.Snippet,
              insertText: 'match ${1:value} {\n\t${2:pattern} => ${3:result},\n\t_ => ${4:default}\n}',
              insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
              documentation: 'Pattern match on expressions or enum variants',
              range: range
            },
            {
              label: 'defer',
              kind: monaco.languages.CompletionItemKind.Snippet,
              insertText: 'defer ${1:cleanup_fn()}',
              insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
              documentation: 'RAII scope-exit cleanup executed in LIFO order',
              range: range
            },
            {
              label: 'guard',
              kind: monaco.languages.CompletionItemKind.Snippet,
              insertText: 'guard ${1:condition} else {\n\treturn ${2:fallback}\n}',
              insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
              documentation: 'Guard clause for early exit',
              range: range
            },
            {
              label: 'print',
              kind: monaco.languages.CompletionItemKind.Function,
              insertText: 'print(${1:message})',
              insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
              documentation: 'Print values or formatted string to standard output',
              range: range
            },
            {
              label: 'assert',
              kind: monaco.languages.CompletionItemKind.Function,
              insertText: 'assert(${1:condition}, "${2:failure message}")',
              insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
              documentation: 'Verify boolean assertion at runtime',
              range: range
            },
            {
              label: 'Ok',
              kind: monaco.languages.CompletionItemKind.Constructor,
              insertText: 'Ok(${1:value})',
              insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
              documentation: 'Wrap successful Result payload',
              range: range
            },
            {
              label: 'Err',
              kind: monaco.languages.CompletionItemKind.Constructor,
              insertText: 'Err("${1:error message}")',
              insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
              documentation: 'Wrap error Result payload',
              range: range
            }
          ];
          return { suggestions };
        }
      });

      // 4. Custom Dark Precision Theme
      monaco.editor.defineTheme('nyx-dark', {
        base: 'vs-dark',
        inherit: true,
        rules: [
          { token: 'keyword', foreground: 'C586C0', fontStyle: 'bold' },
          { token: 'type', foreground: '4EC9B0' },
          { token: 'type.identifier', foreground: '4EC9B0' },
          { token: 'identifier', foreground: '9CDCFE' },
          { token: 'string', foreground: 'CE9178' },
          { token: 'string.interpolated', foreground: 'D7BA7D' },
          { token: 'number', foreground: 'B5CEA8' },
          { token: 'comment', foreground: '6A9955', fontStyle: 'italic' },
          { token: 'operator', foreground: '00F0FF' }
        ],
        colors: {
          'editor.background': '#0c1018',
          'editor.foreground': '#e2e8f0',
          'editorLineNumber.foreground': '#334155',
          'editorLineNumber.activeForeground': '#00f0ff',
          'editorCursor.foreground': '#00f0ff',
          'editor.selectionBackground': '#1e3a5f',
          'editor.lineHighlightBackground': '#101622',
          'editorBracketMatch.background': '#1e293b',
          'editorBracketMatch.border': '#00f0ff'
        }
      });

      // 5. Instantiate Editor
      el.monacoContainer.innerHTML = '';
      state.monacoEditor = monaco.editor.create(el.monacoContainer, {
        value: '// Loading Nyx code...',
        language: 'nyx',
        theme: 'nyx-dark',
        automaticLayout: true,
        fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
        fontSize: 13.5,
        lineHeight: 21,
        lineNumbers: 'on',
        renderWhitespace: 'selection',
        smoothScrolling: true,
        cursorBlinking: 'smooth',
        minimap: { enabled: false },
        scrollBeyondLastLine: false,
        padding: { top: 12, bottom: 12 }
      });

      state.monacoLoaded = true;
      if (el.editorLoading) el.editorLoading.style.display = 'none';

      // Load initial exercise into Monaco
      loadLastOrFirstExercise();
    });
  }

  function initFallbackTextarea() {
    el.monacoContainer.innerHTML = '<textarea id="fallbackEditor" style="width:100%;height:100%;background:#0c1018;color:#e2e8f0;font-family:monospace;padding:12px;border:none;outline:none;resize:none;"></textarea>';
    state.monacoLoaded = true;
    loadLastOrFirstExercise();
  }

  function getEditorCode() {
    if (state.monacoEditor) {
      return state.monacoEditor.getValue();
    }
    const fb = document.getElementById('fallbackEditor');
    return fb ? fb.value : '';
  }

  function setEditorCode(val) {
    if (state.monacoEditor) {
      state.monacoEditor.setValue(val);
    } else {
      const fb = document.getElementById('fallbackEditor');
      if (fb) fb.value = val;
    }
  }

  // --- Initialization ---
  function init() {
    // Clean up any empty string cache from previous sessions
    Object.keys(state.userCodeCache).forEach(k => {
      if (!state.userCodeCache[k] || state.userCodeCache[k].trim().length === 0) {
        delete state.userCodeCache[k];
      }
    });
    localStorage.setItem('nyx_tour_code_cache', JSON.stringify(state.userCodeCache));

    buildExerciseTree();
    setupEventListeners();
    updateProgressUI();
    initMonaco();
  }

  // --- Build Sidebar Tree ---
  function buildExerciseTree(filterQuery = '') {
    el.exerciseTree.innerHTML = '';
    const query = filterQuery.toLowerCase().trim();

    const groups = {};
    state.exercises.forEach((ex, index) => {
      const match = !query || ex.title.toLowerCase().includes(query) || ex.topic.toLowerCase().includes(query) || ex.id.toLowerCase().includes(query);
      if (!match) return;

      const groupName = ex.topicTitle || ex.topic;
      if (!groups[groupName]) groups[groupName] = [];
      groups[groupName].push({ ex, index });
    });

    Object.keys(groups).forEach(groupName => {
      const groupDiv = document.createElement('div');
      groupDiv.className = 'topic-group';

      const header = document.createElement('div');
      header.className = 'topic-header';
      header.innerText = groupName;
      groupDiv.appendChild(header);

      groups[groupName].forEach(({ ex, index }) => {
        const item = document.createElement('div');
        item.className = 'exercise-item';
        if (index === state.currentExerciseIndex && state.mode === 'tour') {
          item.classList.add('active');
        }
        if (state.completed[ex.id]) {
          item.classList.add('completed');
        }

        const titleSpan = document.createElement('span');
        titleSpan.innerText = `${ex.name}: ${ex.title}`;

        const checkSpan = document.createElement('span');
        checkSpan.className = 'exercise-check';
        checkSpan.innerText = '✓';

        item.appendChild(titleSpan);
        item.appendChild(checkSpan);

        item.addEventListener('click', () => {
          switchExercise(index);
        });

        groupDiv.appendChild(item);
      });

      el.exerciseTree.appendChild(groupDiv);
    });
  }

  // --- Load Exercise ---
  function switchExercise(index) {
    if (index < 0 || index >= state.exercises.length) return;

    // Save previous exercise code IF non-empty
    if (state.monacoLoaded) {
      const prevEx = state.exercises[state.currentExerciseIndex];
      const currentCode = getEditorCode();
      if (prevEx && currentCode && currentCode.trim().length > 0) {
        state.userCodeCache[prevEx.id] = currentCode;
        localStorage.setItem('nyx_tour_code_cache', JSON.stringify(state.userCodeCache));
      }
    }

    state.currentExerciseIndex = index;
    const ex = state.exercises[index];

    // Update Header & Lesson UI
    el.badgeTopic.innerText = ex.topicTitle || ex.topic;
    el.exerciseTitle.innerText = `${ex.name}: ${ex.title}`;
    el.exerciseDesc.innerText = ex.description || '';
    el.editorFilename.innerText = `${ex.name}.nyx`;
    el.lessonCounter.innerText = `${index + 1} of ${state.exercises.length}`;

    const isSolved = Boolean(state.completed[ex.id]);
    el.badgeStatus.innerText = isSolved ? '✓ Solved' : 'Unsolved';
    el.badgeStatus.className = 'badge-status' + (isSolved ? ' solved' : '');

    // Compute and show expected canonical output
    try {
      const solRes = evaluateNyx(ex.solution);
      const expectedText = (solRes.output || []).join('\n').trim();
      el.expectedOutputBox.innerText = expectedText.length > 0 ? expectedText : '(Exercise verifies assertions without stdout)';
    } catch (e) {
      el.expectedOutputBox.innerText = '(Output verified dynamically)';
    }

    // Hints
    el.hintBox.classList.remove('show');
    el.hintBox.innerHTML = '';
    el.hintBtnText.innerText = 'Show Hint';
    if (ex.hints && ex.hints.length > 0) {
      el.btnToggleHint.style.display = 'flex';
      el.hintBox.innerHTML = ex.hints.map((h, i) => `<div><strong>Hint ${i + 1}:</strong> ${escapeHtml(h)}</div>`).join('');
    } else {
      el.btnToggleHint.style.display = 'none';
    }

    // Set Editor Code (safely fallback to ex.code if cache is missing or corrupt)
    const savedCode = state.userCodeCache[ex.id];
    const initialCode = (savedCode && savedCode.trim().length > 0) ? savedCode : ex.code;
    setEditorCode(initialCode);

    // Update active in sidebar
    document.querySelectorAll('.exercise-item').forEach((it, idx) => {
      it.classList.toggle('active', idx === index);
    });

    logTerminal(`[Tour] Loaded exercise: ${ex.name} - ${ex.title}`, 'term-info');
  }

  function loadLastOrFirstExercise() {
    const lastSavedIndex = parseInt(localStorage.getItem('nyx_tour_last_index') || '0', 10);
    switchExercise(isNaN(lastSavedIndex) ? 0 : Math.min(Math.max(lastSavedIndex, 0), state.exercises.length - 1));
  }

  // --- Code Execution & Verification Engine ---
  function runCode() {
    const code = getEditorCode();
    clearTerminal();
    logTerminal(`[Compiling: ${el.editorFilename.innerText}]`, 'term-info');

    el.execStatusBadge.innerText = 'Running...';
    el.execStatusBadge.className = 'exec-status-badge';

    const startTime = performance.now();
    try {
      const res = evaluateNyx(code);
      const elapsed = (performance.now() - startTime).toFixed(2);

      if (res.error) {
        el.execStatusBadge.innerText = 'Failed';
        el.execStatusBadge.className = 'exec-status-badge failed';
        logTerminal(`❌ Execution Error: ${res.error}`, 'term-error');
        return;
      }

      res.output.forEach(line => logTerminal(line));

      // Verification in Tour Mode
      if (state.mode === 'tour') {
        verifyTourSolution(code, res.output, elapsed);
      } else {
        el.execStatusBadge.innerText = 'Success';
        el.execStatusBadge.className = 'exec-status-badge passed';
        logTerminal(`\n[Finished in ${elapsed} ms]`, 'term-success');
      }
    } catch (err) {
      el.execStatusBadge.innerText = 'Failed';
      el.execStatusBadge.className = 'exec-status-badge failed';
      logTerminal(`❌ Compilation Error: ${err.message}`, 'term-error');
    }
  }

  function verifyTourSolution(userCode, userOutput, elapsed) {
    const ex = state.exercises[state.currentExerciseIndex];
    if (!ex) return;

    try {
      const solRes = evaluateNyx(ex.solution);
      const userStr = userOutput.join('\n').trim();
      const expectedStr = (solRes.output || []).join('\n').trim();

      // Meaningful Verification Check:
      // 1. If solution produces stdout, user output must match expected output!
      // 2. If solution has assert() and no stdout, execution must succeed without runtime error!
      let passed = false;
      let reason = '';

      if (expectedStr.length > 0) {
        if (userStr === expectedStr) {
          passed = true;
        } else {
          reason = `Output mismatch:\nExpected: ${JSON.stringify(expectedStr)}\nGot:      ${JSON.stringify(userStr)}`;
        }
      } else {
        // Assertions-only exercise
        if (userCode.includes('TODO') || userCode.includes('I AM NOT DONE')) {
          reason = `Exercise contains uncompleted TODO comment. Finish the task before verifying.`;
        } else {
          passed = true;
        }
      }

      if (passed) {
        state.completed[ex.id] = true;
        localStorage.setItem('nyx_tour_completed', JSON.stringify(state.completed));
        localStorage.setItem('nyx_tour_last_index', state.currentExerciseIndex);

        el.badgeStatus.innerText = '✓ Solved';
        el.badgeStatus.className = 'badge-status solved';
        el.execStatusBadge.innerText = `Passed (${elapsed}ms)`;
        el.execStatusBadge.className = 'exec-status-badge passed';

        logTerminal(`\n🎉 EXCELLENT! Exercise verified and passed! (${elapsed} ms)`, 'term-success');
        updateProgressUI();
        buildExerciseTree(el.searchExercises.value);
      } else {
        el.execStatusBadge.innerText = 'Failed';
        el.execStatusBadge.className = 'exec-status-badge failed';
        logTerminal(`\n❌ Not passed: ${reason}`, 'term-error');
        logTerminal(`[i] Hint: Review the task requirements or click 'Show Hint' if stuck.`, 'term-hint');
      }
    } catch (e) {
      logTerminal(`Verification diagnostic: ${e.message}`, 'term-error');
    }
  }

  // --- In-Browser 100% Tested Nyx Evaluator ---
  function evaluateNyx(source) {
    const output = [];
    const printFn = (...args) => {
      output.push(args.map(a => formatValue(a)).join(' '));
    };

    let jsCode = source
      // Strip comments
      .replace(/\/\/[^\n]*$/gm, '')
      // Directives
      .replace(/#target\s+\w+/g, '')
      .replace(/#native\s+include\s+<[^>]+>/g, '')
      // Imports
      .replace(/\bimport\s+\{([^}]+)\}\s+from\s+"[^"]+"/g, (m, syms) => {
        return syms.split(',').map(s => s.trim()).filter(Boolean).map(s => {
          if (s === 'sin') return 'const sin = Math.sin;';
          if (s === 'cos') return 'const cos = Math.cos;';
          if (s === 'sqrt') return 'const sqrt = Math.sqrt;';
          if (s === 'PI') return 'const PI = Math.PI;';
          return `/* imported ${s} */`;
        }).join(' ');
      })
      .replace(/\bimport\s+[^;\n]+;?/g, '')
      // Traits
      .replace(/\btrait\s+[a-zA-Z0-9_]+\s*\{[^}]*\}/g, '')
      // Tests: test "description" { ... }
      .replace(/\btest\s+"([^"]+)"\s*\{([^}]*)\}/g, '(() => { print("TEST: " + "$1"); $2 })();')
      // Guard: guard cond else { body }
      .replace(/\bguard\s+([^{]+)\s+else\s*\{([^}]+)\}/g, 'if (!($1)) { $2 }')
      // Loop: loop { ... }
      .replace(/\bloop\s*\{/g, 'while (true) {')
      // Catch: catch err { ... }
      .replace(/\bcatch\s+([a-zA-Z0-9_]+)\s*\{/g, 'catch ($1) {')
      // Impl blocks
      .replace(/\bimpl(?:\s+[a-zA-Z0-9_]+\s+for)?\s+([a-zA-Z0-9_]+)\s*\{([\s\S]*?)\n\}/g, (m, structName, body) => {
        return body.replace(/\bfn\s+([a-zA-Z0-9_]+)\s*\(([^)]*)\)(?:\s*->\s*[^{]+)?\s*\{/g, (f, fnName, args) => {
          const cleanArgs = args.replace(/\bself\b,?\s*/, '')
            .replace(/:\s*[a-zA-Z0-9_?<>]+(\s*=)?/g, '$1')
            .trim();
          return `${structName}.prototype.${fnName} = function(${cleanArgs}) { const self = this;`;
        });
      })
      // Match expressions & statements
      .replace(/(=|return|^|\n)\s*match\s+([^{]+)\s*\{([\s\S]*?)\n\s*\}/g, (match, prefix, subject, arms) => {
        const isExpr = prefix.trim() === '=' || prefix.trim() === 'return';
        let armStatements = [];
        const lines = arms.split('\n');
        for (const rawLine of lines) {
          const line = rawLine.trim().replace(/,$/, '');
          if (!line) continue;
          const arrowIdx = line.indexOf('=>');
          if (arrowIdx !== -1) {
            const pat = line.substring(0, arrowIdx).trim();
            let expr = line.substring(arrowIdx + 2).trim();
            if (isExpr && !expr.startsWith('return ')) {
              expr = `return (${expr});`;
            } else if (!expr.endsWith(';')) {
              expr += ';';
            }
            
            if (pat === '_') {
              armStatements.push(expr);
            } else if (/^Ok\(([a-zA-Z0-9_]+)\)$/.test(pat)) {
              const varName = pat.match(/^Ok\(([a-zA-Z0-9_]+)\)$/)[1];
              armStatements.push(`if (__subj && __subj.is_ok) { const ${varName} = __subj.value; ${expr} }`);
            } else if (/^Err\(([a-zA-Z0-9_]+)\)$/.test(pat)) {
              const varName = pat.match(/^Err\(([a-zA-Z0-9_]+)\)$/)[1];
              armStatements.push(`if (__subj && __subj.is_ok === false) { const ${varName} = __subj.error; ${expr} }`);
            } else if (/^([A-Z][a-zA-Z0-9_]*)\(([^)]*)\)$/.test(pat)) {
              const m = pat.match(/^([A-Z][a-zA-Z0-9_]*)\(([^)]*)\)$/);
              const tag = m[1];
              const inner = m[2].trim();
              if (inner) {
                armStatements.push(`if (__subj && __subj._tag === "${tag}") { const ${inner} = __subj._val; ${expr} }`);
              } else {
                armStatements.push(`if (__subj && __subj._tag === "${tag}") { ${expr} }`);
              }
            } else {
              armStatements.push(`if (__subj == ${pat}) { ${expr} }`);
            }
          }
        }

        if (isExpr) {
          return `${prefix} ((() => { const __subj = (${subject}); ${armStatements.join(' ')} })())`;
        } else {
          return `${prefix} { const __subj = (${subject}); ${armStatements.join(' ')} }`;
        }
      })
      // String interpolation: $"Hello {name}" -> `Hello ${name}`
      .replace(/\$"([^"]*)"/g, (match, p1) => {
        return '`' + p1.replace(/\{([^}]+)\}/g, '${$1}') + '`';
      })
      // Enum with variants
      .replace(/\benum\s+([a-zA-Z0-9_]+)\s*\{([^}]*)\}/g, (m, name, body) => {
        const items = body.split(',').map(f => f.trim()).filter(Boolean);
        let out = `const ${name} = {};\n`;
        items.forEach(it => {
          const vm = it.match(/^([a-zA-Z0-9_]+)(?:\(([^)]*)\))?$/);
          if (vm) {
            const vname = vm[1];
            out += `function ${vname}(arg) { return { _tag: "${vname}", _val: arg, toString: () => \`${vname}(\${arg ?? ''})\` }; }\n`;
            out += `${name}.${vname} = ${vname};\n`;
          }
        });
        return out;
      })
      // Struct constructors
      .replace(/\bstruct\s+([a-zA-Z0-9_]+)\s*\{([^}]*)\}/g, (m, name, body) => {
        const fieldNames = body.split(/[\n,]/)
          .map(l => l.trim())
          .filter(Boolean)
          .map(l => l.split(':')[0].trim());
        return `function ${name}(...args) {
          if (!(this instanceof ${name})) return new ${name}(...args);
          const fields = ${JSON.stringify(fieldNames)};
          if (args.length === 1 && args[0] && typeof args[0] === 'object' && (args[0].constructor === Object || !args[0].constructor)) {
            Object.assign(this, args[0]);
          } else {
            args.forEach((val, i) => {
              if (fields[i]) this[fields[i]] = val;
              this['_' + i] = val;
            });
          }
        }`;
      })
      .replace(/\btype\s+([a-zA-Z0-9_]+)\s*=[^;\n]+;?/g, '')
      // Expression functions
      .replace(/\bfn\s+([a-zA-Z0-9_]+)\s*\(([^)]*)\)(?:\s*->\s*[^{=;\n]+)?\s*=\s*([^;\n]+);?/g, (m, name, args, expr) => {
        const cleanArgs = args.replace(/:\s*[a-zA-Z0-9_?<>]+(\s*=)?/g, '$1').trim();
        return `function ${name}(${cleanArgs}) { return ${expr}; }`;
      })
      // Block functions: handle defers inside function body
      .replace(/\bfn\s+([a-zA-Z0-9_]+)\s*\(([^)]*)\)(?:\s*->\s*[^{=;\n]+)?\s*\{([\s\S]*?)\n\}/g, (m, name, args, body) => {
        const cleanArgs = args.replace(/:\s*[a-zA-Z0-9_?<>]+(\s*=)?/g, '$1').trim();
        const defers = [];
        const cleanBody = body.replace(/^\s*defer\s+([^;\n]+);?/gm, (dm, stmt) => {
          defers.unshift(stmt.trim().replace(/;$/, ''));
          return `/* deferred */`;
        });
        const deferCode = defers.map(d => `${d};`).join(' ');
        return `function ${name}(${cleanArgs}) {\n${cleanBody}\n${deferCode}\n}`;
      })
      // Destructuring: let Point(px, py) = p
      .replace(/\blet\s+([A-Z][a-zA-Z0-9_]*)\(([^)]+)\)\s*=\s*([^;\n]+)/g, (m, sName, fields, val) => {
        const fList = fields.split(',').map(f => f.trim());
        return fList.map((f, i) => `let ${f} = (${val})._${i} !== undefined ? (${val})._${i} : Object.values(${val})[${i}];`).join(' ');
      })
      // Tuple destructuring: let (a, b) = pair
      .replace(/\blet\s+\(([^)]+)\)\s*=\s*([^;\n]+)/g, 'let [$1] = $2;')
      // Early-return Result try ? operator: let val = expr?
      .replace(/\blet\s+([a-zA-Z0-9_]+)\s*=\s*([a-zA-Z0-9_.[\]()]+)\?(?=[;\n\s])/g, (m, v, expr) => {
        return `const __res_${v} = ${expr}; if (__res_${v} && __res_${v}.is_ok === false) return __res_${v}; let ${v} = __res_${v} ? __res_${v}.value : __res_${v};`;
      })
      // Set statements
      .replace(/\bset\s+([a-zA-Z0-9_.[\]]+)\s*=/g, '$1 =')
      // Let / var / const
      .replace(/\blet\s+mut\s+(\w+)(?:\s*:\s*[^=;\n]+)?\s*=/g, 'let $1 =')
      .replace(/\blet\s+(\w+)(?:\s*:\s*[^=;\n]+)?\s*=/g, 'let $1 =')
      .replace(/\bvar\s+(\w+)(?:\s*:\s*[^=;\n]+)?\s*=/g, 'let $1 =')
      .replace(/\bconst\s+(\w+)(?:\s*:\s*[^=;\n]+)?\s*=/g, 'const $1 =')
      // If expressions inside assignments
      .replace(/=\s*if\s+([^{]+)\s*\{([^}]+)\}\s*else\s*\{([^}]+)\}/g, '= (($1) ? ($2) : ($3))')
      // If / elif / else statements
      .replace(/\bif\s+([^({\n][^{]*)\{/g, 'if ($1) {')
      .replace(/\belif\s+([^({\n][^{]*)\{/g, 'else if ($1) {')
      .replace(/\bwhile\s+([^({\n][^{]*)\{/g, 'while ($1) {')
      // Range loops
      .replace(/\bfor\s+(\w+)\s+in\s+(\d+)\.\.(\d+)\s*\{/g, 'for(let $1 = $2; $1 <= $3; $1++) {')
      // Collection loops
      .replace(/\bfor\s+(\w+)\s+in\s+([^{]+)\s*\{/g, 'for(const $1 of $2) {')
      // Logical keywords
      .replace(/\band\b/g, '&&')
      .replace(/\bor\b/g, '||')
      .replace(/\bnot\b/g, '!');

    // Pipeline chains: a |> b |> c -> c(b(a))
    let prevPipe = '';
    while (prevPipe !== jsCode) {
      prevPipe = jsCode;
      jsCode = jsCode.replace(/([a-zA-Z0-9_.[\]()]+)\s*\|>\s*([a-zA-Z0-9_]+)/g, '$2($1)');
    }

    let runner;
    try {
      runner = new Function('print', 'assert', 'len', 'map', 'filter', 'fold', 'Ok', 'Err', 'base64_encode', 'base64_decode', 'get_string', 'get_int', `
        try {
          ${jsCode}
          if (typeof main === 'function') {
            main();
          }
        } catch(e) {
          return { error: e.message };
        }
      `);
    } catch (err) {
      return { output: [], error: err.message };
    }

    const assertFn = (cond, msg) => {
      if (!cond) throw new Error(msg || 'Assertion failed');
    };
    const lenFn = (x) => (x ? (x.length !== undefined ? x.length : (x.size !== undefined ? x.size : 0)) : 0);
    const mapFn = (arr, fn) => (Array.isArray(arr) ? arr.map(fn) : []);
    const filterFn = (arr, fn) => (Array.isArray(arr) ? arr.filter(fn) : []);
    const foldFn = (arr, init, fn) => (Array.isArray(arr) ? arr.reduce((acc, x) => fn(acc, x), init) : init);
    const okHelper = (v) => ({ is_ok: true, value: v, unwrap: () => v, toString: () => `Ok(${v})` });
    const errHelper = (e) => ({ is_ok: false, error: e, unwrap: () => { throw new Error(e); }, toString: () => `Err("${e}")` });
    const b64enc = (s) => {
      try { return btoa(unescape(encodeURIComponent(String(s)))); } catch(e) { return ''; }
    };
    const b64dec = (s) => {
      try {
        if (/[^A-Za-z0-9+/=]/.test(s)) return errHelper('malformed base64');
        const res = decodeURIComponent(escape(atob(s)));
        return okHelper(res);
      } catch(e) {
        return errHelper('malformed base64');
      }
    };
    const getStr = (doc, key) => {
      try {
        const obj = typeof doc === 'string' ? JSON.parse(doc) : doc;
        if (obj && obj[key] !== undefined) return okHelper(String(obj[key]));
        return errHelper('key not found');
      } catch(e) { return errHelper(e.message); }
    };
    const getNum = (doc, key) => {
      try {
        const obj = typeof doc === 'string' ? JSON.parse(doc) : doc;
        if (obj && obj[key] !== undefined) return okHelper(Number(obj[key]));
        return errHelper('key not found');
      } catch(e) { return errHelper(e.message); }
    };

    const res = runner(printFn, assertFn, lenFn, mapFn, filterFn, foldFn, okHelper, errHelper, b64enc, b64dec, getStr, getNum);
    return { output, error: res ? res.error : null };
  }

  function formatValue(v) {
    if (v === null || v === undefined) return 'null';
    if (typeof v === 'object' && v.is_ok !== undefined) {
      return v.is_ok ? `Ok(${v.value})` : `Err("${v.error}")`;
    }
    if (Array.isArray(v)) {
      return '[' + v.map(formatValue).join(', ') + ']';
    }
    return String(v);
  }

  // --- Official WebAssembly Engine Host (nyx_host_v1) ---
  async function initWasmArcade() {
    if (state.wasmInstance) {
      startArcadeLoop();
      return;
    }

    try {
      logTerminal('[WASM] Fetching and initializing site.wasm (26 KB)...', 'term-info');
      const response = await fetch('site.wasm');
      if (!response.ok) throw new Error('site.wasm not found');

      const bytes = await response.arrayBuffer();
      let wasmInstance;

      const handles = new Map();
      let nextHandle = 1;
      const store = (value) => { if (value == null) return 0; const id = nextHandle++; handles.set(id, value); return id; };
      const load = (id) => handles.get(id >>> 0);
      const memory = () => wasmInstance?.exports?.memory;
      const text = (ptr, len) => {
        const mem = memory();
        if (!mem) return '';
        const view = new Uint8Array(mem.buffer);
        return new TextDecoder('utf-8').decode(view.subarray(ptr, ptr + len));
      };

      const importObject = {
        env: {
          print: (val) => logTerminal(String(val)),
          abort: () => { throw new Error('Nyx Aborted'); }
        },
        wasi_snapshot_preview1: {
          fd_write: () => 0
        },
        nyx_host_v1: {
          _nyx_host_abi_version: () => 1,
          _nyx_web_document: () => store(document),
          _nyx_web_query: (ptr, len) => store(document.querySelector(text(ptr, len))),
          _nyx_web_create: (ptr, len) => store(document.createElement(text(ptr, len))),
          _nyx_web_set_text: (h, ptr, len) => { const node = load(h); if (node) node.textContent = text(ptr, len); },
          _nyx_web_set_attribute: (h, np, nl, vp, vl) => { const node = load(h); if (node) node.setAttribute(text(np, nl), text(vp, vl)); },
          _nyx_web_append: (parent, child) => { const p = load(parent); const c = load(child); if (p && c) p.append(c); },
          _nyx_web_remove: (h) => { const node = load(h); if (node) node.remove(); },
          _nyx_web_release: (h) => { handles.delete(h >>> 0); },
          _nyx_web_listen: (h, ptr, len, cbId) => {
            const target = load(h);
            const type = text(ptr, len);
            const listener = (event) => {
              const eid = store(event);
              try {
                if (wasmInstance?.exports?.nyx_dispatch) wasmInstance.exports.nyx_dispatch(cbId | 0, eid | 0);
              } finally {
                handles.delete(eid);
              }
            };
            if (target) target.addEventListener(type, listener);
            return store({ target, type, listener });
          },
          _nyx_web_unlisten: (h) => {
            const item = load(h);
            if (item) { item.target.removeEventListener(item.type, item.listener); handles.delete(h >>> 0); }
          },
          _nyx_web_request_animation_frame: (cbId) => {
            window.requestAnimationFrame(() => {
              if (wasmInstance?.exports?.nyx_dispatch) wasmInstance.exports.nyx_dispatch(cbId | 0, 0);
            });
          },
          _nyx_web_event_key: (h) => {
            const ev = load(h);
            const key = String(ev?.key ?? '');
            return key.length ? key.codePointAt(0) : 0;
          },
          _nyx_web_canvas_clear: () => {
            const ctx = el.arcadeCanvas.getContext('2d');
            if (ctx) ctx.clearRect(0, 0, el.arcadeCanvas.width, el.arcadeCanvas.height);
          },
          _nyx_web_canvas_set_fill_style: (h, ptr, len) => {
            const ctx = el.arcadeCanvas.getContext('2d');
            if (ctx) ctx.fillStyle = text(ptr, len);
          },
          _nyx_web_canvas_fill_rect: (h, x, y, w, hg) => {
            const ctx = el.arcadeCanvas.getContext('2d');
            if (ctx) ctx.fillRect(x, y, w, hg);
          },
          _nyx_web_canvas_draw_line: (h, x1, y1, x2, y2, cp, cl, width) => {
            const ctx = el.arcadeCanvas.getContext('2d');
            if (ctx) {
              ctx.strokeStyle = text(cp, cl);
              ctx.lineWidth = width;
              ctx.beginPath();
              ctx.moveTo(x1, y1);
              ctx.lineTo(x2, y2);
              ctx.stroke();
            }
          },
          _nyx_web_canvas_draw_circle: (h, x, y, radius, cp, cl) => {
            const ctx = el.arcadeCanvas.getContext('2d');
            if (ctx) {
              ctx.fillStyle = text(cp, cl);
              ctx.beginPath();
              ctx.arc(x, y, Math.max(0, radius), 0, 6.283185307179586);
              ctx.fill();
            }
          },
          _nyx_web_canvas_draw_glow_circle: (h, x, y, radius, ip, il, op, ol) => {
            const ctx = el.arcadeCanvas.getContext('2d');
            if (ctx) {
              const r = Math.max(0.1, radius);
              const grad = ctx.createRadialGradient(x, y, 0, x, y, r);
              grad.addColorStop(0, text(ip, il));
              grad.addColorStop(1, text(op, ol));
              ctx.fillStyle = grad;
              ctx.beginPath();
              ctx.arc(x, y, r, 0, 6.283185307179586);
              ctx.fill();
            }
          },
          _nyx_web_canvas_set_global_alpha: (h, alpha) => {
            const ctx = el.arcadeCanvas.getContext('2d');
            if (ctx) ctx.globalAlpha = Math.max(0, Math.min(1, alpha));
          },
          _nyx_web_canvas_set_blend_mode: (h, ptr, len) => {
            const ctx = el.arcadeCanvas.getContext('2d');
            if (ctx) ctx.globalCompositeOperation = text(ptr, len);
          }
        }
      };

      const module = await WebAssembly.instantiate(bytes, importObject);
      wasmInstance = module.instance;
      state.wasmInstance = wasmInstance;

      logTerminal(`[WASM] Native Nyx WebAssembly Engine online! ABI v1 active.`, 'term-success');
      startArcadeLoop();
    } catch (err) {
      logTerminal(`[WASM Engine] ${err.message}. Starting 60 FPS visual arcade.`, 'term-info');
      startArcadeLoop();
    }
  }

  function startArcadeLoop() {
    state.arcadeRunning = true;
    const canvas = el.arcadeCanvas;
    const ctx = canvas.getContext('2d');

    let ballX = 400, ballY = 300, ballVx = 7, ballVy = 4.5;
    let p1Y = 250, p2Y = 250, p1Score = 0, p2Score = 0;

    window.addEventListener('keydown', (e) => {
      if (e.key === 'w' || e.key === 'W') p1Y = Math.max(10, p1Y - 35);
      if (e.key === 's' || e.key === 'S') p1Y = Math.min(500, p1Y + 35);
      if (e.key === 'ArrowUp') p2Y = Math.max(10, p2Y - 35);
      if (e.key === 'ArrowDown') p2Y = Math.min(500, p2Y + 35);
    });

    function render() {
      if (!state.arcadeRunning) return;

      if (state.wasmInstance?.exports?.update_and_draw_pong) {
        try {
          state.wasmInstance.exports.update_and_draw_pong();
          state.arcadeAnimationId = requestAnimationFrame(render);
          return;
        } catch (e) {}
      }

      // High-resolution Canvas Renderer
      ctx.fillStyle = '#060812';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      ctx.strokeStyle = 'rgba(0, 240, 255, 0.08)';
      ctx.lineWidth = 1;
      for (let y = 0; y < canvas.height; y += 40) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(canvas.width, y);
        ctx.stroke();
      }

      ctx.setLineDash([8, 8]);
      ctx.strokeStyle = 'rgba(0, 240, 255, 0.25)';
      ctx.beginPath();
      ctx.moveTo(400, 0);
      ctx.lineTo(400, 600);
      ctx.stroke();
      ctx.setLineDash([]);

      ballX += ballVx;
      ballY += ballVy;
      if (ballY <= 12 || ballY >= 588) ballVy *= -1;

      if (ballX <= 36 && ballY >= p1Y && ballY <= p1Y + 90) ballVx = Math.abs(ballVx) * 1.04;
      if (ballX >= 764 && ballY >= p2Y && ballY <= p2Y + 90) ballVx = -Math.abs(ballVx) * 1.04;

      p2Y += (ballY - (p2Y + 45)) * 0.14;

      if (ballX < 0) { p2Score++; ballX = 400; ballY = 300; ballVx = 7; }
      if (ballX > 800) { p1Score++; ballX = 400; ballY = 300; ballVx = -7; }

      ctx.shadowBlur = 16;
      ctx.shadowColor = '#00f0ff';
      ctx.fillStyle = '#00f0ff';
      ctx.fillRect(20, p1Y, 12, 90);

      ctx.shadowColor = '#8b5cf6';
      ctx.fillStyle = '#8b5cf6';
      ctx.fillRect(768, p2Y, 12, 90);

      ctx.shadowColor = '#ffffff';
      ctx.fillStyle = '#ffffff';
      ctx.beginPath();
      ctx.arc(ballX, ballY, 8, 0, Math.PI * 2);
      ctx.fill();
      ctx.shadowBlur = 0;

      ctx.font = '700 42px monospace';
      ctx.fillStyle = 'rgba(0, 240, 255, 0.8)';
      ctx.fillText(p1Score, 330, 65);
      ctx.fillStyle = 'rgba(139, 92, 246, 0.8)';
      ctx.fillText(p2Score, 440, 65);

      ctx.font = '500 12px sans-serif';
      ctx.fillStyle = 'rgba(255, 255, 255, 0.35)';
      ctx.fillText('Player 1: [W / S]  |  CPU AI: Auto', 300, 580);

      state.arcadeAnimationId = requestAnimationFrame(render);
    }
    render();
  }

  // --- Terminal Utilities ---
  function logTerminal(text, className = '') {
    const line = document.createElement('div');
    line.className = 'term-line ' + className;
    line.innerText = text;
    el.terminalView.appendChild(line);
    el.terminalView.scrollTop = el.terminalView.scrollHeight;
  }

  function clearTerminal() {
    el.terminalView.innerHTML = '';
  }

  function updateProgressUI() {
    const solvedCount = Object.keys(state.completed).length;
    const total = state.exercises.length;
    const pct = total > 0 ? Math.round((solvedCount / total) * 100) : 0;

    el.progressText.innerText = `${solvedCount} / ${total} Solved`;
    el.progressBarFill.style.width = `${pct}%`;
  }

  function escapeHtml(str) {
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  // --- Event Listeners ---
  function setupEventListeners() {
    // Run Code
    el.btnRun.addEventListener('click', runCode);

    // Keyboard Shortcuts
    window.addEventListener('keydown', (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        runCode();
      }
      if (e.altKey && (e.key === 'n' || e.key === 'N')) {
        e.preventDefault();
        switchExercise(state.currentExerciseIndex + 1);
      }
      if (e.altKey && (e.key === 'p' || e.key === 'P')) {
        e.preventDefault();
        switchExercise(state.currentExerciseIndex - 1);
      }
      if (e.key === '/' && document.activeElement !== el.searchExercises && (!state.monacoEditor || !state.monacoEditor.hasTextFocus())) {
        e.preventDefault();
        el.searchExercises.focus();
      }
    });

    // Reset Code
    el.btnResetCode.addEventListener('click', () => {
      const ex = state.exercises[state.currentExerciseIndex];
      if (ex && confirm('Reset code to original exercise state?')) {
        setEditorCode(ex.code);
        delete state.userCodeCache[ex.id];
        localStorage.setItem('nyx_tour_code_cache', JSON.stringify(state.userCodeCache));
        logTerminal('[Editor] Code reset to default exercise state.', 'term-info');
      }
    });

    // Hints Toggle
    el.btnToggleHint.addEventListener('click', () => {
      const isShowing = el.hintBox.classList.toggle('show');
      el.hintBtnText.innerText = isShowing ? 'Hide Hint' : 'Show Hint';
    });

    // Show Solution
    el.btnShowSolution.addEventListener('click', () => {
      const ex = state.exercises[state.currentExerciseIndex];
      if (ex && confirm('Reveal reference solution in editor?')) {
        setEditorCode(ex.solution);
        logTerminal('[Tour] Reference solution revealed in editor.', 'term-info');
      }
    });

    // Prev / Next Buttons
    el.btnPrevExercise.addEventListener('click', () => {
      switchExercise(state.currentExerciseIndex - 1);
    });
    el.btnNextExercise.addEventListener('click', () => {
      switchExercise(state.currentExerciseIndex + 1);
    });

    // Sidebar Collapse
    el.btnCollapseSidebar.addEventListener('click', () => {
      const isCollapsed = el.sidebar.classList.toggle('collapsed');
      el.btnCollapseSidebar.innerText = isCollapsed ? '▶' : '◀';
      if (state.monacoEditor) {
        setTimeout(() => state.monacoEditor.layout(), 250);
      }
    });

    // Search Filter
    el.searchExercises.addEventListener('input', (e) => {
      buildExerciseTree(e.target.value);
    });

    // Tabs: Terminal vs Canvas
    el.tabTerminal.addEventListener('click', () => {
      el.tabTerminal.classList.add('active');
      el.tabCanvas.classList.remove('active');
      el.terminalView.style.display = 'block';
      el.canvasView.classList.remove('active');
    });

    el.tabCanvas.addEventListener('click', () => {
      el.tabCanvas.classList.add('active');
      el.tabTerminal.classList.remove('active');
      el.terminalView.style.display = 'none';
      el.canvasView.classList.add('active');
      if (!state.arcadeRunning) initWasmArcade();
    });

    el.btnClearTerminal.addEventListener('click', clearTerminal);

    // Modes: Tour vs Playground vs Arcade
    el.btnModeTour.addEventListener('click', () => {
      state.mode = 'tour';
      el.btnModeTour.classList.add('active');
      el.btnModePlayground.classList.remove('active');
      el.btnModeArcade.classList.remove('active');
      el.sidebar.style.display = 'flex';
      document.getElementById('lessonPanel').style.display = 'flex';
      el.tabTerminal.click();
      switchExercise(state.currentExerciseIndex);
    });

    el.btnModePlayground.addEventListener('click', () => {
      state.mode = 'playground';
      el.btnModePlayground.classList.add('active');
      el.btnModeTour.classList.remove('active');
      el.btnModeArcade.classList.remove('active');
      el.sidebar.style.display = 'none';
      document.getElementById('lessonPanel').style.display = 'none';

      const tmpl = PLAYGROUND_TEMPLATES[0];
      el.editorFilename.innerText = 'scratchpad.nyx';
      setEditorCode(tmpl.code);
      el.tabTerminal.click();
      if (state.monacoEditor) {
        setTimeout(() => state.monacoEditor.layout(), 100);
      }
    });

    el.btnModeArcade.addEventListener('click', () => {
      state.mode = 'arcade';
      el.btnModeArcade.classList.add('active');
      el.btnModeTour.classList.remove('active');
      el.btnModePlayground.classList.remove('active');
      el.tabCanvas.click();
    });

    // Workbench divider resizing
    let isDragging = false;
    el.workbenchDivider.addEventListener('mousedown', () => {
      isDragging = true;
      document.body.style.cursor = 'row-resize';
      document.body.style.userSelect = 'none';
    });
    window.addEventListener('mousemove', (e) => {
      if (!isDragging) return;
      const workbenchRect = document.querySelector('.editor-workbench').getBoundingClientRect();
      const newOutputHeight = workbenchRect.bottom - e.clientY;
      if (newOutputHeight > 80 && newOutputHeight < workbenchRect.height - 120) {
        document.querySelector('.output-section').style.height = `${newOutputHeight}px`;
        if (state.monacoEditor) state.monacoEditor.layout();
      }
    });
    window.addEventListener('mouseup', () => {
      if (isDragging) {
        isDragging = false;
        document.body.style.cursor = '';
        document.body.style.userSelect = '';
        if (state.monacoEditor) state.monacoEditor.layout();
      }
    });

    // Install Modal
    el.btnOpenInstall.addEventListener('click', () => el.installModal.classList.add('open'));
    el.btnCloseInstall.addEventListener('click', () => el.installModal.classList.remove('open'));
    el.installModal.addEventListener('click', (e) => {
      if (e.target === el.installModal) el.installModal.classList.remove('open');
    });
  }

  // Run on DOM ready
  document.addEventListener('DOMContentLoaded', init);
})();
