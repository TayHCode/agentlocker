# Install and connect details

Details behind the [README quickstart](../README.md): cloning without GitHub
credentials, platform notes, the optional gateway prerequisites and the exact
client entries.

For one library reachable from local agents and hosted bots, follow the
[self-host quickstart](self-host.md).

## Download and check

Download the ZIP or tar archive from [agentlocker.dev](https://agentlocker.dev/#download)
and extract it into a permanent directory. Run `python3 hub.py doctor` and
`python3 hub.py serve` there, then open the printed local address for setup.
The archive includes the application and setup wizard, with no Git history,
private deployment configuration or imported library. Python 3.11+ is required;
Git is optional for archives. On Windows use Python 3.12.4+ and replace
`python3` with `py -3` or `python`. The [Windows quickstart](../README.md#quickstart)
includes source download and extraction commands that need no Git or winget.

## Development checkout

Install Git and Python 3.11+ (Windows: 3.12.4+). Run
`gh repo clone <OWNER>/agentlocker` (or `git clone <HTTPS_URL> agentlocker`)
with your existing GitHub login, then `cd agentlocker`. Replace `<OWNER>` and
`<HTTPS_URL>` with your approved repository; an SSH URL needs an SSH key.
No GitHub credentials on this machine? For a private transfer from an approved
machine, run `git bundle create agentlocker.bundle <APPROVED_BRANCH>`, copy the file here, run
`git clone --branch <APPROVED_BRANCH> agentlocker.bundle agentlocker`, then
`git -C agentlocker remote set-url origin <HTTPS_URL>`. All commands run from
that checkout; `<HUB_DIR>` means its absolute directory.

A bundle includes the selected ref's reachable history. It can contain private
information removed from current files; selecting one ref does not sanitize it.
Review and approve its contents before transfer, keep it private, and complete
the [history privacy gate](release.md#release-gates) before public distribution.
Do not use development recovery bundles as public installation packages.

```sh
python3 hub.py doctor
```

The application needs no Python packages. The complete developer test suite
requires the [contributing prerequisites](../CONTRIBUTING.md), including Pillow,
tzdata, Node and the checkout's CI/maintainer files.
Contributors must also run `python3 hub.py check`, which enforces the
maintainer commit-email policy. `doctor` checks the installed catalog without
requiring your own commits to use the maintainer's identity.

## Platforms

Windows: use `py -3` (or `python`) in place of `python3`. The private store
is owner-only on Windows only with Python 3.12.4+; older versions leave it
with the parent folder's permissions, so use 3.12.4+ there.

macOS and Linux use `python3`. The gateway is not available on Windows; use the
stdio route (`mcp_endpoint.py`, below) there.

## Optional: shared authenticated tools

Skip this for catalog-only use. Install Node 20+ (Node 24 recommended), npm and
the system `ss` utility first (Linux). On the Node 20 line, use 20.19 or newer
for the locked dependencies; the current pins are verified on Node 24. Check with
`node --version`, `npm --version` and `ss --version`. macOS uses the built-in `lsof`. The gateway
is not available on Windows. The installer creates private directories and
installs only `@samanhappy/mcphub@1.1.7` from the tracked
`gateway/package-lock.json` (`npm ci --ignore-scripts`). First installation needs
registry access and installs third-party dependencies. Review server definitions
before starting: start executes their commands. The shipped `example-server`
runs locally with Python and exposes `add`; see [gateway setup](gateway.md) for
a tool-call verification command.

```sh
python3 gateway.py install
python3 gateway.py prepare && python3 gateway.py start
python3 gateway.py status
```

The single streamable HTTP endpoint is `/mcp` on numeric IPv4 loopback, port
43871 by default. If that port is busy, leave its listener alone and run
`python3 gateway.py start --port <PORT>` instead, replacing `<PORT>` with an
unused unprivileged port. Below, `<GATEWAY_URL>` means that complete local URL;
the wizard's Connect your agents screen shows it. Only local processes should
access it. Bearer-token authentication is opt-in with `gateway.py start --require-token`;
see [gateway authentication](gateway.md) for private token export and client setup.
Stop it when finished:

```sh
python3 gateway.py stop
```

## Client entries

Merge the chosen entries into existing settings, reload the agent and approve the
connection. `python3 hub.py connect` prints them; `python3 hub.py connect --write`
merges only locker entries after confirmation and a timestamped backup. These
match the wizard's Connect your agents screen with private paths and URLs
replaced by placeholders. The catalog lists content; the optional gateway
executes tools. The gateway fragments below apply without `--require-token`;
when it is enabled, rerun `hub.py connect` for entries that reference the token
environment variable.

Claude Code project `.mcp.json` and Cursor project `.cursor/mcp.json` — catalog:

```json
{
  "mcpServers": {
    "agentlocker": {
      "command": "python3",
      "args": ["<HUB_DIR>/mcp_endpoint.py"]
    }
  }
}
```

Codex approved `config.toml` — catalog:

```toml
[mcp_servers.agentlocker]
command = "python3"
args = ["<HUB_DIR>/mcp_endpoint.py"]
```

Claude Code `.mcp.json` — optional gateway:

```json
{
  "mcpServers": {
    "agentlocker-gateway": {
      "type": "http",
      "url": "<GATEWAY_URL>"
    }
  }
}
```

Cursor `.cursor/mcp.json` — optional gateway:

```json
{
  "mcpServers": {
    "agentlocker-gateway": {
      "url": "<GATEWAY_URL>"
    }
  }
}
```

Codex `config.toml` — optional gateway:

```toml
[mcp_servers.agentlocker-gateway]
url = "<GATEWAY_URL>"
```

See [client configuration](clients.md) for per-client paths.

## Verify in your agent

Ask the agent to list the connected MCP tools and call `hub_list_skills` (also
available: `hub_list_rules`, `hub_list_mcp_servers`, `hub_list_routines`,
`hub_list_plugins`, `hub_list_connections`). The result should match
`manifest.json` plus `.hub-store/catalog/manifest.json`. Read a skill, rule or
routine with `hub_get_item` (`kind` is `skill`, `rule` or `routine`, plus its
`name`). If using the gateway, inspect its separate tool list and call a harmless
imported tool; catalog discovery alone does not prove tool execution or shared
auth.

Credentials and gateway state live in gitignored `.hub-store/` (directories 700,
files 600); the npm runtime lives in gitignored `.scratch/`. `.hub-store/` and
local `config.json` must never be committed. See [MCP authentication](mcp-auth.md).

## Troubleshooting

- Health check fails: read the named failure and fix it before importing; rerun `python3 hub.py doctor`. Maintainers also run `hub.py check`.
- Wizard unavailable: rerun `python3 hub.py serve`, use its newly printed URL, and keep the terminal open.
- Gateway fails: check Node/runtime prerequisites and declared Store secrets for imported servers; use `python3 gateway.py status` and the redacted `.hub-store/gateway/gateway.log`.
- Tools absent: replace placeholders, preserve the configuration wrapper, reload and approve the client; revisit Connect your agents after starting the gateway.
- Auth expired: reconnect in the wizard's sign-in screen, then run `python3 gateway.py refresh`; clients must reconnect. Stored manual credentials are not provider-tested.
