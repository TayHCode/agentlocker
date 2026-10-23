# agentlocker

One place to share skills and routine instructions across your AI agents. Scan what
your agents already have, import it into a private local catalog, and connect each
agent to that catalog over MCP. Setup needs Python; Git is optional for archive
installs. No Python packages to install.
MIT licensed; see [LICENSE](LICENSE).

Release status: self-hosted source preview. [Download it](https://agentlocker.dev/#download)
with the v4 setup wizard. Cross-agent synthetic acceptance is recorded; an
independent human setup trial remains unverified.
See the [evidence and release gates](docs/release.md).

To share the library with hosted bots as well as local agents, follow the
[self-host setup](docs/self-host.md). Existing Composio MCPs stay in Composio.

## Quickstart

Use a permanent source directory and Python 3.11+ (Windows: Python 3.12.4+;
use `py -3` instead of `python3`). Get the approved source using the
[install instructions](docs/install.md).

On a stock Windows x64 machine, install Python 3.12.4 or newer from
[Python for Windows](https://www.python.org/downloads/windows/). In the installer,
enable **Add python.exe to PATH**, then open a new PowerShell window. Download
and extract the source into a new permanent directory:

```powershell
python --version
Invoke-WebRequest https://github.com/TayHCode/agentlocker/archive/refs/heads/main.zip -OutFile agentlocker.zip
Expand-Archive agentlocker.zip -DestinationPath agentlocker-source
Set-Location agentlocker-source\agentlocker-main
python hub.py doctor
python hub.py serve
```

`doctor` must exit successfully before setup. An archive install prints that Git
is optional and still checks the catalog and private installation state. These
commands do not require Git, winget, or a PowerShell execution-policy change.
Use `python` in place of `python3` in the commands below.

For the guided scan → import → connect interface, run `python3 hub.py serve`
and open the local URL printed in your terminal. The CLI steps follow below.

1. **Check and import your library.** The scan finds existing agent content;
   import lets you choose what to copy into the private catalog.

   ```sh
   python3 hub.py doctor
   python3 hub.py scan --import
   python3 hub.py list
   ```

2. **Connect your local agents.** Review the printed entries, then confirm
   the write. Existing settings are preserved; changed files are backed up.

   ```sh
   python3 hub.py connect --agent claude codex
   python3 hub.py connect --agent claude codex --write
   ```

   For Cursor, OpenCode and other local clients, use the
   [client instructions](docs/clients.md).

3. **Use the library.** Ask a connected agent:

   > Find a skill in agentlocker, read its supporting files, and use it for my task.
   > List the routines and read one when I ask you to follow it.

   To reach the same library from a hosted bot, complete the one-time
   [self-host setup](docs/self-host.md), publish it, and connect the bot to your
   catalog URL. Claude Code, Codex CLI and Grok Bot have recorded acceptance
   evidence; other clients have their own support limits.

Edit the original item and re-import it to update the local library. Publish
again to update hosted readers. Each agent fetches the current content rather
than maintaining a separate substantive copy.

## Imports and links

Shipped entries are indexed in [manifest.json](manifest.json). In the manual
client examples, `<HUB_DIR>` is your permanent installation directory.

Single items: `python3 hub.py import-skill <path>`, `python3 hub.py import-rule <path.md>`,
`python3 hub.py import-routine <file.json>`, `python3 hub.py import-mcp <file.json>`;
options `--owner O`, `--origin L`, `--name N`. Definitions use `secret://<name>` references, never values
([MCP auth](docs/mcp-auth.md)). Preview with
`python3 hub.py link --target <root> --dry-run`, then run without `--dry-run`.
`python3 hub.py remove <kind> <name> --yes` removes an import; re-importing a
changed source keeps the old copy in `.hub-store/history/`.

## Routines

A routine is saved instructions for recurring work, with a suggested schedule.
Import it once; ask any connected agent to fetch it and follow its current
prompt. Importing does not turn on a timer.

Automatic timing is optional and belongs to the chosen runner. See
[routine scheduling](docs/routines.md) when you need it. Existing Composio
connections can stay as they are. Optional [skill links](docs/reference.md) and
the [shared-tools gateway](docs/gateway.md) are separate from this setup.

Contributors must run `python3 hub.py check` and the Python test suite.
The installation's `doctor` command does not replace maintainer source checks.
See [contributing](CONTRIBUTING.md) for the test dependencies and commands.

## Limitations

The hosted endpoint shares a read-only catalog. Skills, rules and routine prompts
include their supporting files; plugin and connection records describe setup,
and MCP records describe servers. Reading a record does not install a plugin,
authenticate a provider or execute an upstream MCP tool. The optional local
gateway runs configured upstream tools on its host. Automatic scheduling belongs
to each runner and is separate from fetching a routine's current instructions.

Claude Code and Codex CLI have controlled synthetic acceptance evidence. Grok
Bot reads and updates are user-reported. Other clients must support the relevant
MCP transport and authorization flow; they have not all been tested. Each
self-hosted deployment currently serves one owner's catalog, and authorized
clients can read all published entries. Managed hosting is planned, not available.

## Remote catalog

The optional Cloudflare Worker serves an owner-only, read-only catalog for
hosted bots. Set your deployment's `public_url` using the [self-host guide](docs/self-host.md);
each client needs its own OAuth grant. Source merges do not deploy the Worker
or publish local imports. Deployment and real-client acceptance have separate
[release gates](docs/release.md#release-gates). See [remote catalog](docs/remote.md),
[Composio](docs/composio.md) and the [Grok Bot bridge](docs/grok-bot-bootstrap.md).

## Reference

- [Overview](docs/OVERVIEW.md) and [vision](VISION.md); the MCP endpoint is `mcp_endpoint.py`
- [Install details](docs/install.md), [commands](docs/cli.md), [imports and links](docs/reference.md), [file formats](docs/formats.md)
- [Guided import](docs/IMPORT-PROMPT.md), [scanner](docs/scan.md), [safety scan](docs/safety.md), [wizard](docs/ui.md), [client setup](docs/clients.md)
- [Gateway](docs/gateway.md), [gateway research](docs/mcp-gateway.md), [Executor](docs/executor-connector.md), [agents sync](docs/agents-sync.md)
- [Related projects](docs/related.md), [factory overlap](docs/factory-overlap.md), [hosted catalog](docs/hosted-later.md), [acceptance](docs/acceptance.md)
- [Release candidate and evidence](docs/release.md)
- [Changelog](CHANGELOG.md) and [security reporting](SECURITY.md)
