'use strict';

const { resolveNyxCommand } = require('./server_options');

const NATIVE_REQUIREMENT =
    'Nyx cpp builds require Clang++, GCC/G++, or MSVC cl with C++20 support. ' +
    'Put the compiler on PATH or set NYX_CXX; run “Nyx: Toolchain Doctor” to verify it.';

const PROJECT_LINKS = Object.freeze({
    repository: 'https://github.com/justsomeone-e/nyx',
    documentation: 'https://github.com/justsomeone-e/nyx#readme',
    releases: 'https://github.com/justsomeone-e/nyx/releases',
    roadmap: 'https://github.com/justsomeone-e/nyx/blob/main/docs/internals/ROADMAP_AND_BACKEND_GATES.md',
    issues: 'https://github.com/justsomeone-e/nyx/issues/new'
});

const LINK_COMMANDS = Object.freeze([
    ['nyx.openRepository', 'GitHub repository', PROJECT_LINKS.repository],
    ['nyx.openDocumentation', 'documentation', PROJECT_LINKS.documentation],
    ['nyx.openReleases', 'release history', PROJECT_LINKS.releases],
    ['nyx.openRoadmap', 'compiler roadmap', PROJECT_LINKS.roadmap],
    ['nyx.reportIssue', 'issue reporter', PROJECT_LINKS.issues]
]);

function sourceTarget(document) {
    const match = document.getText().match(/^\s*#target\s+([A-Za-z0-9_]+)/m);
    return match ? match[1].toLowerCase() : 'cpp';
}

async function requireNyxDocument(vscode) {
    const editor = vscode.window.activeTextEditor;
    if (!editor || editor.document.languageId !== 'nyxlang') {
        await vscode.window.showWarningMessage('Open a .nyx file before running a Nyx command.');
        return undefined;
    }
    if (editor.document.isUntitled || !editor.document.uri.fsPath) {
        await vscode.window.showWarningMessage('Save the Nyx file before running it.');
        return undefined;
    }
    if (editor.document.isDirty && !(await editor.document.save())) {
        return undefined;
    }
    return editor.document;
}

function taskScope(vscode, document) {
    if (document) {
        const folder = vscode.workspace.getWorkspaceFolder(document.uri);
        if (folder) return folder;
    }
    if (vscode.workspace.workspaceFolders && vscode.workspace.workspaceFolders.length > 0) {
        return vscode.workspace.workspaceFolders[0];
    }
    return vscode.TaskScope.Global;
}

async function executeTask(vscode, action, document, target) {
    const configuredCli = vscode.workspace.getConfiguration('nyx.server').get('path', 'nyx');
    const cli = resolveNyxCommand(configuredCli);
    const args = [action];
    if (document) args.push(document.uri.fsPath);
    if (target && target !== 'source' && (action === 'run' || action === 'build')) {
        args.push('--target', target);
    }

    const label = action === 'doctor'
        ? 'Nyx: Toolchain Doctor'
        : `Nyx: ${action[0].toUpperCase()}${action.slice(1)} ${document.uri.path.split('/').pop()}`;
    const task = new vscode.Task(
        { type: 'nyx', action },
        taskScope(vscode, document),
        label,
        'nyx',
        new vscode.ShellExecution(cli, args),
        []
    );
    if (action === 'build') {
        task.group = vscode.TaskGroup.Build;
    }
    task.presentationOptions = {
        reveal: vscode.TaskRevealKind.Always,
        panel: vscode.TaskPanelKind.Shared,
        clear: false,
        focus: true,
        showReuseMessage: false
    };
    return vscode.tasks.executeTask(task);
}

async function maybeExplainNativeRequirement(vscode, context, action, document, configuredTarget) {
    if (action !== 'run' && action !== 'build') return true;
    const target = configuredTarget === 'source' ? sourceTarget(document) : configuredTarget;
    if (target !== 'cpp' && target !== 'cpp' && target !== 'native') return true;
    const key = 'nyx.cppRequirementAcknowledged';
    if (context.globalState.get(key, false)) return true;

    const choice = await vscode.window.showInformationMessage(
        NATIVE_REQUIREMENT,
        'Continue',
        'Run Toolchain Doctor'
    );
    await context.globalState.update(key, true);
    if (choice === 'Run Toolchain Doctor') {
        await executeTask(vscode, 'doctor');
        return false;
    }
    return true;
}

async function openProjectLink(vscode, label, url) {
    const opened = await vscode.env.openExternal(vscode.Uri.parse(url));
    if (!opened) {
        await vscode.window.showWarningMessage(`Could not open the Nyx ${label}: ${url}`);
    }
}

function registerNyxCommands(vscode, context) {
    const registrations = [];
    for (const [commandId, action] of [
        ['nyx.runCurrentFile', 'run'],
        ['nyx.buildCurrentFile', 'build'],
        ['nyx.checkCurrentFile', 'check']
    ]) {
        registrations.push(vscode.commands.registerCommand(commandId, async () => {
            const document = await requireNyxDocument(vscode);
            if (!document) return;
            const configuredTarget = vscode.workspace
                .getConfiguration('nyx.run')
                .get('target', 'source');
            if (!(await maybeExplainNativeRequirement(
                vscode, context, action, document, configuredTarget
            ))) return;
            await executeTask(vscode, action, document, configuredTarget);
        }));
    }
    registrations.push(vscode.commands.registerCommand('nyx.toolchainDoctor', async () => {
        await executeTask(vscode, 'doctor');
    }));
    for (const [commandId, label, url] of LINK_COMMANDS) {
        registrations.push(vscode.commands.registerCommand(commandId, async () => {
            await openProjectLink(vscode, label, url);
        }));
    }

    const runButton = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 100);
    runButton.name = 'Run Nyx File';
    runButton.text = '$(play) Nyx';
    runButton.tooltip = 'Run the active Nyx file in the integrated terminal';
    runButton.command = 'nyx.runCurrentFile';
    runButton.show();
    registrations.push(runButton);

    context.subscriptions.push(...registrations);
    return registrations;
}

module.exports = {
    LINK_COMMANDS,
    NATIVE_REQUIREMENT,
    PROJECT_LINKS,
    executeTask,
    openProjectLink,
    registerNyxCommands,
    sourceTarget
};
