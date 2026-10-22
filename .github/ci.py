import argparse
import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
GATEWAY_TESTS = {
    'test_example_server.ExampleServerTests.test_shipped_definition_through_mcphub',
    'test_verify.RealGatewayTests.test_example_server_live_ui_check_and_calls',
    'test_gateway_guard.LiveGatewayGuardTests.test_non_loopback_host_is_refused_while_loopback_client_works',
    'test_gateway_guard.LiveGatewayGuardTests.test_required_token_gates_mcp_and_the_env_file_token_works',
    'test_gateway_guard.LiveGatewayGuardTests.test_restart_without_the_flag_removes_the_requirement',
}
WINDOWS_SKIPS = {
    'test_local_catalog_proof.LocalCatalogProofTests.test_symlinked_tmpdir_accepts_canonical_fixture_endpoint',
    'test_agents_sync.AgentsSyncTests.test_protected_targets_include_account_database_home_under_changed_home',
    'test_connect.ConnectTests.test_write_failure_names_client_and_continues',
    'test_connect.ConnectTests.test_write_failure_flushes_stdout_before_stderr',
    'test_connect.ConnectOutputTests.test_interpreter_prefers_a_working_python3_on_path',
    'test_gateway_adapter.AdapterTests.test_stale_pid_does_not_identify_current_process',
    'test_gateway_install.InstallTests.test_failed_npm_restores_umask',
    'test_gateway_install.InstallTests.test_port_probe_allows_time_wait',
    'test_scanner_crontab.CrontabReadTests.test_denied_crontab_read_is_reported_not_silent',
    'test_scanner_crontab.CrontabReadTests.test_timed_out_crontab_read_is_reported',
    'test_scanner_crontab.CrontabReadTests.test_missing_crontab_binary_is_reported',
    'test_scanner_crontab.CrontabReadTests.test_no_crontab_for_user_stays_silent',
    'test_scanner_crontab.CrontabReadTests.test_readable_crontab_is_imported',
    'test_scanner_isolation.ScanIsolationTests.test_live_flag_enables_crontab_and_executor',
    'test_scanner_isolation.ScanIsolationTests.test_real_home_stays_live',
    'test_v12_import_regressions.SourceHomePathBindingRegressions.test_scan_import_and_runtime_launch_resolve_source_home_command',
    'test_routine_enable.RoutineEnableTests.test_changed_owned_file_refuses_disable',
    'test_routine_enable.RoutineEnableTests.test_cron_concurrent_changes_are_preserved',
    'test_routine_enable.RoutineEnableTests.test_cron_enable_disable_idempotency_and_backup',
    'test_routine_enable.RoutineEnableTests.test_end_to_end_shipped_inventory_cron_executes_pinned_prompt',
    'test_routine_enable.RoutineEnableTests.test_failed_native_install_rolls_back_files',
    'test_routine_enable.RoutineEnableTests.test_launchd_plist_native_calls_and_disable',
    'test_routine_enable.RoutineEnableTests.test_missing_agent_refuses_before_native_install',
    'test_routine_enable.RoutineEnableTests.test_modified_cron_entry_is_preserved',
    'test_routine_enable.RoutineEnableTests.test_state_write_failure_restores_cron_and_owned_files',
    'test_routine_enable.RoutineEnableTests.test_symlinked_destination_is_refused',
    'test_routine_enable.RoutineEnableTests.test_systemd_files_native_calls_and_disable',
    'test_routine_enable.RoutineEnableTests.test_update_backs_up_prompt_and_keeps_single_cron_job',
}
WINDOWS_ACL = 'test_store_windows_acl.WindowsStoreAclTests.test_store_is_owner_only_and_secret_inherits_it'


def environment(root):
    base = root / '.scratch/ci'
    home, temporary, binary = (base / name for name in ('home', 'tmp', 'bin'))
    values = {
        'HOME': str(home), 'USERPROFILE': str(home),
        'APPDATA': str(home / 'AppData/Roaming'),
        'LOCALAPPDATA': str(home / 'AppData/Local'),
        'XDG_CONFIG_HOME': str(home / '.config'),
        'XDG_DATA_HOME': str(home / '.local/share'),
        'XDG_STATE_HOME': str(home / '.local/state'),
        'XDG_CACHE_HOME': str(home / '.cache'),
        'CODEX_HOME': '', 'CLAUDE_CONFIG_DIR': '',
        'TMPDIR': str(temporary), 'TEMP': str(temporary), 'TMP': str(temporary),
        'PYTHONUTF8': '1', 'PYTHONDONTWRITEBYTECODE': '1',
        'PYTHONPATH': str(base / 'deps'),
    }
    for directory in (home, temporary, binary):
        directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    if os.name != 'nt':
        stub = binary / 'crontab'
        stub.write_text('#!/bin/sh\necho "no crontab for fixture" >&2\nexit 1\n', encoding='utf-8')
        stub.chmod(0o700)
    return values, binary


def setup():
    values, binary = environment(ROOT)
    with open(os.environ['GITHUB_ENV'], 'a', encoding='utf-8') as stream:
        stream.writelines(f'{key}={value}\n' for key, value in values.items())
    with open(os.environ['GITHUB_PATH'], 'a', encoding='utf-8') as stream:
        stream.write(str(binary) + '\n')


def runtime():
    minimum = (3, 12, 4) if sys.platform == 'win32' else (3, 11)
    if sys.version_info < minimum:
        raise RuntimeError('CI requires Python 3.11+, or 3.12.4+ on Windows')
    print(sys.version)
    for tool in ('node', 'npm', 'git', 'bash'):
        executable = shutil.which(tool)
        if not executable:
            raise RuntimeError(f'{tool} is required on the runner PATH')
        version = subprocess.check_output([executable, '--version'], text=True).strip()
        print(f'{tool}: {version.splitlines()[0]}')
        if tool == 'node' and int(version.lstrip('v').split('.')[0]) != 24:
            raise RuntimeError('CI requires Node 24')


def skipped_unexpectedly(result, gateway=False, platform=sys.platform):
    allowed = set() if gateway else set(GATEWAY_TESTS)
    if not gateway:
        allowed.update(WINDOWS_SKIPS if platform == 'win32' else {WINDOWS_ACL})
    return [(test.id(), reason) for test, reason in result.skipped if test.id() not in allowed]


def cases(suite):
    for test in suite:
        if isinstance(test, unittest.TestSuite):
            yield from cases(test)
        else:
            yield test


def run_tests(gateway=False):
    minimum = (3, 12, 4) if sys.platform == 'win32' else (3, 11)
    if sys.version_info < minimum:
        raise RuntimeError('CI requires Python 3.11+, or 3.12.4+ on Windows for private-store ACLs')
    if not shutil.which('node'):
        raise RuntimeError('Node is required for UI smoke coverage')
    if not gateway and any(importlib.util.find_spec(name) is None for name in ('PIL', 'tzdata')):
        raise RuntimeError('Install pillow and tzdata before running CI tests')
    sys.path.insert(0, str(ROOT))
    suite = unittest.defaultTestLoader.discover(str(ROOT / 'tests'))
    if gateway:
        selected = [test for test in cases(suite) if test.id() in GATEWAY_TESTS]
        if {test.id() for test in selected} != GATEWAY_TESTS:
            raise RuntimeError('Required live gateway tests were not discovered')
        suite = unittest.TestSuite(selected)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    unexpected = skipped_unexpectedly(result, gateway)
    for test_id, reason in unexpected:
        print(f'Unexpected skip: {test_id}: {reason}', file=sys.stderr)
    expected_count = len(result.skipped) - len(unexpected)
    summary = f'Ran {result.testsRun} tests; {expected_count} expected/platform skips; {len(unexpected)} unexpected skips'
    print(summary)
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a', encoding='utf-8') as stream:
            stream.write(summary + '\n')
    return 0 if result.testsRun and result.wasSuccessful() and not unexpected else 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=('setup', 'runtime', 'tests'))
    parser.add_argument('--gateway', action='store_true')
    args = parser.parse_args()
    if args.command == 'runtime':
        runtime()
        return 0
    if args.command == 'setup':
        setup()
        return 0
    return run_tests(args.gateway)


if __name__ == '__main__':
    raise SystemExit(main())
