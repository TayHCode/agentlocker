# Use agentlocker

Read [VISION.md](VISION.md) and follow [docs/formats.md](docs/formats.md).

- For guided scan → import → connect setup, use [the import prompt](docs/IMPORT-PROMPT.md).
- Discover owned entries in `manifest.json`; load `skills/<name>/SKILL.md` only when relevant. Keep each skill's supporting files together.
- Read applicable fragments in `rules/`, including `rules/shared-policy.md`. Preserve the closest project's instructions.
- Start the read-only MCP endpoint with `python3 mcp_endpoint.py` over stdio. Discover its `hub_list_*` tools through MCP tools/list; use them to list skills, rules, routines and MCP server definitions. Listing does not execute upstream servers.
- Read routine definitions under `routines/<id>/routine.json`. Keep portable definitions `enabled=false`, with one owner and one preferred runner. Import records definitions only. `hub.py routine enable <id> --runner <runner>` previews local installation or a platform handoff; local writes require `--write` plus `--yes` or interactive confirmation. Enablement state belongs in the local store; hosted activation remains a user action in that platform. See [docs/routines.md](docs/routines.md).
- Read nonsecret MCP definitions under `mcp/servers/`. Use `secret://<name>` references. Never ask for secret values in chat, print them, or resolve them through the listing endpoint. Use the approved private auth flow in [docs/mcp-auth.md](docs/mcp-auth.md).
- Preview links with `python3 hub.py link --target <root> --dry-run`; materialize approved links with `python3 hub.py link --target <root>`. `python3 hub.py link --home` links into `~/.claude/skills` and `~/.agents/skills` only when the user asks for it. Preserve unfamiliar destination files and inspect conflicts.
- Inspect imports with `python3 hub.py list`. `python3 hub.py remove <kind> <name>` deletes only imported items you own, after `--yes` or confirmation; it never removes shipped items. Re-importing a changed source with the same owner and origin updates it and keeps the previous copy under `.hub-store/history/`.
- Run `python3 hub.py check` and `python3 -m unittest discover -s tests -v`. Report actual commands, exit codes, test counts and unverified claims. Inside an agent sandbox `hub.py check` is the gate; if the sandbox denies localhost sockets, `ps` or `crontab`, run the full suite outside the sandbox and say so in the report.
- `python3 hub.py doctor` is the installation health command for self-hosters, including source snapshots and their own Git identities. It does not replace the required maintainer `check` gate or its commit-email policy.
- Commit with the repository-local identity: `git config user.email` must print an address from `config/commit-email-allowlist.txt` (set it with `git -C <checkout> config user.email <address>`; use the repo-local setting, not global). Check it before committing in any worktree, and never change author or committer email by hand. `hub.py check` requires allowlisted authors and committers, except the exact GitHub web-flow committer (`noreply` at `github.com`) with an allowlisted author. See [docs/cli.md](docs/cli.md) for verified PR-range handling.
- Keep changes within the requested scope. Preserve user files and existing product account configuration. Obtain authorization before destructive operations, external writes, publishing, schedules or service changes unless the current task already authorizes that exact action.
- Keep secrets, local store contents and machine-specific configuration outside Git. Use one declared maintainer per item; import copies with provenance instead of silently replacing another owner's source.

## Grok Bot

Use the [bootstrap bridge](docs/grok-bot-bootstrap.md). A hosted skill must be enabled per bot; filesystem links do not populate its hosted library. Do not create a hosted skill or activate a routine merely by reading this hub.

## Client connection exception

Setup prints client settings by default. `python3 hub.py connect --write` is an
opt-in exception: after `--yes` or interactive confirmation it backs up and
merges only `agentlocker` / `agentlocker-gateway` into detected user configs.
Preserve all other client settings; reject symlinked or non-ordinary destinations.
Builders must prove writes only in temporary fixture homes; real configs remain
read-only during development. `hub.py scan --import` points to `hub.py connect`.

## Routine enablement

`python3 hub.py routine enable` and `disable` also default to print-only.
Use `--write` plus `--yes` or interactive confirmation to install or remove
owned cron entries, systemd user units, launchd LaunchAgents, Windows Task
Scheduler tasks, or a Claude Code scheduled skill. Preserve foreign files and modified jobs; back up every changed
artifact. Store per-runner records in the configured local store, never flip the
shipped definition. Hosted exports do not activate schedules. Builders must use
fixture homes and fake scheduler binaries; no real user services during development.
