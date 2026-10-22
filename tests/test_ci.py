import importlib.util
import os
import re
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('ci_gate', ROOT / '.github/ci.py')
ci = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ci)


class CIGateTests(unittest.TestCase):
    def workflow_jobs(self):
        workflow = (ROOT / '.github/workflows/ci.yml').read_text(encoding='utf-8')
        jobs = workflow.split('\njobs:\n', 1)[1]
        return workflow, dict(re.findall(r'^  ([a-z-]+):\n(.*?)(?=^  [a-z-]+:\n|\Z)', jobs, re.M | re.S))

    def test_public_workflow_is_manual_only_with_read_only_permissions(self):
        workflow, jobs = self.workflow_jobs()
        self.assertEqual(workflow.split('\non:\n', 1)[1].split('\npermissions:', 1)[0].strip(),
                         'workflow_dispatch:')
        self.assertEqual(workflow.split('\npermissions:\n', 1)[1].split('\nconcurrency:', 1)[0].strip(),
                         'contents: read')
        self.assertEqual(set(jobs), {'test', 'remote'})
        self.assertEqual(workflow.count('permissions:'), 1)
        for forbidden in ('self-hosted', 'secrets.', 'TRUSTED_BASE', 'EVENT_BASE',
                          'git fetch', 'Clean workspace', 'pull_request_target', 'environment:',
                          'services:', 'container:', 'continue-on-error:', 'if:'):
            self.assertNotIn(forbidden, workflow)
        self.assertIn('group: ci-${{ github.workflow }}-${{ github.ref }}', workflow)
        self.assertIn('cancel-in-progress: false', workflow)

    def test_hosted_jobs_pin_runtimes_and_test_dependencies(self):
        workflow, jobs = self.workflow_jobs()
        self.assertEqual(re.findall(r'^    runs-on: (.+)$', workflow, re.M),
                         ['${{ matrix.os }}', 'ubuntu-latest'])
        self.assertIn('        os: [ubuntu-latest, macos-latest, windows-latest]\n', jobs['test'])
        self.assertIn('      fail-fast: false\n', jobs['test'])
        for job in jobs.values():
            self.assertIn('      - uses: actions/setup-python@v5\n        with:\n'
                          "          python-version: '3.12'\n", job)
            self.assertIn('      - uses: actions/setup-node@v4\n        with:\n'
                          "          node-version: '24'\n", job)
            self.assertIn('run: python .github/ci.py runtime\n', job)
        self.assertIn('run: python -m pip install --target .scratch/ci/deps '
                      'Pillow==13.0.0 tzdata==2026.5\n', jobs['test'])

    def test_checkouts_use_full_history_without_persisted_credentials(self):
        _, jobs = self.workflow_jobs()
        for job in jobs.values():
            self.assertEqual(job.count('uses: actions/checkout@'), 1)
            checkout = job.split('      - uses: actions/checkout@', 1)[1].split('      - ', 1)[0]
            self.assertIn('          fetch-depth: 0\n', checkout)
            self.assertIn('          persist-credentials: false\n', checkout)
            self.assertNotIn('          ref:', checkout)
            self.assertNotIn('          token:', checkout)

    def test_fixture_setup_precedes_tests_and_hub_check(self):
        workflow, jobs = self.workflow_jobs()
        self.assertIn("  PYTHONUTF8: '1'\n  PYTHONDONTWRITEBYTECODE: '1'\n", workflow)
        test = jobs['test']
        commands = re.findall(r'^        run: (.+)$', test, re.M)
        self.assertEqual(commands, [
            'python .github/ci.py runtime', 'python .github/ci.py setup',
            'python -m pip install --target .scratch/ci/deps Pillow==13.0.0 tzdata==2026.5',
            'python .github/ci.py tests', 'python hub.py check',
        ])
        self.assertNotIn('working-directory:', test)
        self.assertNotIn('env:', test)

    def test_remote_keeps_npm_checks_in_fixture_environment(self):
        _, jobs = self.workflow_jobs()
        remote = jobs['remote']
        self.assertIn('    defaults:\n      run:\n        working-directory: remote\n', remote)
        self.assertEqual(re.findall(r'^      - run: (.+)$', remote, re.M),
                         ['npm ci', 'npm run typecheck', 'npm test'])
        self.assertEqual(re.findall(r'^        run: (.+)$', remote, re.M),
                         ['python .github/ci.py runtime', 'python .github/ci.py setup'])
        self.assertLess(remote.index('run: python .github/ci.py setup'), remote.index('- run: npm ci'))
        self.assertEqual(remote.count('working-directory: ${{ github.workspace }}'), 2)
        for command in ('runtime', 'setup'):
            self.assertIn('        working-directory: ${{ github.workspace }}\n'
                          '        run: python .github/ci.py ' + command + '\n', remote)
        self.assertNotIn('env:', remote)

    def test_commit_text_range_scans_messages_and_rejects_unreadable_history(self):
        from checks import commit_text

        message = 'New head ' + 'workstation' + '-' + str(473)
        responses = ['fixture', 'false', 'base-id', 'head-id', 'base-id', 'head-id', message]
        with patch.object(commit_text, 'git', side_effect=responses) as git, \
                patch.object(commit_text, 'local_patterns', return_value=([], [])):
            errors, count = commit_text.scan_range(ROOT, 'base', 'HEAD')
        self.assertEqual(count, 1)
        self.assertTrue(any('private-device-label' in error for error in errors))
        self.assertIn(unittest.mock.call(Path('fixture'), 'rev-list', 'base-id..head-id'), git.call_args_list)
        with patch.object(commit_text, 'git', side_effect=ValueError('unreadable history')):
            with self.assertRaisesRegex(ValueError, 'unreadable history'):
                commit_text.scan_range(ROOT, 'missing', 'HEAD')

    def test_runtime_rejects_wrong_node_major(self):
        with patch.object(ci.sys, 'version_info', (3, 12, 10)), \
                patch.object(ci.shutil, 'which', return_value='node'), \
                patch.object(ci.subprocess, 'check_output', return_value='v22.0.0'):
            with self.assertRaisesRegex(RuntimeError, 'Node 24'):
                ci.runtime()

    def test_missing_runtime_skip_is_rejected_by_live_gate(self):
        test = SimpleNamespace(id=lambda: next(iter(ci.GATEWAY_TESTS)))
        result = SimpleNamespace(skipped=[(test, 'runtime absent')])
        self.assertEqual(ci.skipped_unexpectedly(result), [])
        self.assertEqual(len(ci.skipped_unexpectedly(result, gateway=True)), 1)

    def test_windows_acl_and_missing_node_cannot_silently_skip(self):
        acl = SimpleNamespace(id=lambda: ci.WINDOWS_ACL)
        node = SimpleNamespace(id=lambda: 'test_ui_scan.ScanUITests.test_static_xss_safe_and_node_smoke')
        result = SimpleNamespace(skipped=[(acl, 'no ACL'), (node, 'no Node')])
        self.assertEqual(len(ci.skipped_unexpectedly(result, platform='win32')), 2)
        self.assertEqual(ci.skipped_unexpectedly(result, platform='linux'), [(node.id(), 'no Node')])

    def test_windows_platform_skips_do_not_hide_linux_regressions(self):
        test = SimpleNamespace(id=lambda: next(iter(ci.WINDOWS_SKIPS)))
        result = SimpleNamespace(skipped=[(test, 'POSIX only')])
        self.assertEqual(ci.skipped_unexpectedly(result, platform='win32'), [])
        self.assertEqual(len(ci.skipped_unexpectedly(result, platform='linux')), 1)

    def test_empty_or_renamed_live_suite_fails_closed(self):
        with patch.object(ci.sys, 'version_info', (3, 12, 10)), patch.object(ci.shutil, 'which', return_value='node'), \
                patch.object(ci.unittest.defaultTestLoader, 'discover', return_value=unittest.TestSuite()):
            with self.assertRaisesRegex(RuntimeError, 'not discovered'):
                ci.run_tests(gateway=True)

    def test_setup_only_emits_paths_inside_fixture(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            envfile, pathfile = root / 'env', root / 'path'
            with patch.object(ci, 'ROOT', root), patch.dict(os.environ, {
                    'GITHUB_ENV': str(envfile), 'GITHUB_PATH': str(pathfile)}):
                ci.setup()
            values = dict(line.split('=', 1) for line in envfile.read_text(encoding='utf-8').splitlines())
            for key in ('HOME', 'USERPROFILE', 'APPDATA', 'LOCALAPPDATA', 'XDG_CONFIG_HOME', 'TMPDIR', 'TEMP', 'TMP'):
                self.assertTrue(Path(values[key]).is_relative_to(root))
            self.assertEqual(values['CODEX_HOME'], '')
            self.assertEqual(values['CLAUDE_CONFIG_DIR'], '')
            self.assertEqual(Path(pathfile.read_text(encoding='utf-8').strip()), root / '.scratch/ci/bin')

    def test_skip_allowlist_names_exist_in_discovered_suite(self):
        suite = unittest.TestLoader().discover(str(ROOT / 'tests'))
        names = {test.id() for test in ci.cases(suite)}
        self.assertEqual((ci.GATEWAY_TESTS | ci.WINDOWS_SKIPS | {ci.WINDOWS_ACL}) - names, set())

    def test_routine_native_skips_are_allowed_only_on_windows(self):
        names = {name for name in ci.WINDOWS_SKIPS if name.startswith('test_routine_enable.')}
        self.assertTrue(names)
        result = SimpleNamespace(skipped=[(SimpleNamespace(id=lambda name=name: name), 'POSIX fixture') for name in names])
        self.assertEqual(ci.skipped_unexpectedly(result, platform='win32'), [])
        self.assertEqual(len(ci.skipped_unexpectedly(result, platform='linux')), len(names))
