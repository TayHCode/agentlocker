# agentlocker — Vision

agentlocker is its own thing: put your skills, MCPs, routines, everything you use; as easily as possible accepted by any agent (Grok Bot, OpenAI agents, Muse, Codex, Claude, OpenCode, anything).

- **MCP auth lives once in the hub.** MCP auth/OAuth is done once in the hub; every agent uses it without re-authenticating. Tokens live in the hub's local store, NEVER in the repo (gitignored, never printed).
- **v1: self-hosted, reachable across agents.** A repository can hold the source, but setup must make the catalog reachable from the user's local agents and hosted bots. An owner-operated remote endpoint is a delivery option; a managed cloud service for multiple users is a separate later decision.
- **Keep the first release simple.** Share skills and routine instructions through one catalog. Agents fetch and execute them on request; optional scheduling stays with the chosen runner.
- **Built for agents first.** The only human-facing part is setup: easy import of skills, routines/schedules, existing MCPs, and MCP auth; then point agents at it.

## Design consequences (non-normative)

- Everything an agent needs is discoverable from the repo root without a human: `AGENTS.md`, a machine-readable manifest, and plain `SKILL.md` packages.
- Secrets and OAuth tokens are only ever referenced by name (for example `secret://<name>`); values live in a gitignored local store outside version control.
- The same manifest must be servable later from a hosted MCP endpoint, so nothing in the format may assume a local filesystem path.

> The project is named **agentlocker** ("Agent Hub" was an earlier placeholder name).

## North star

> make it as stupid simple and easy as possible for someone to import all skills, routines, mcp, connections, plugins, etc etc etc. Then have them reachable from any agent they have. That's it.

## Product acceptance

The motivating request is one easy place to centralize skills and routines
across agents, including hosted bots, while existing MCPs can stay in Composio.
Another user must be able to set it up and use the same maintained content
across agents without orchestrator-specific repository instructions or manual
copies of every skill. A personal checkout with two local catalog readers is
an engineering milestone, not completion of that request.

See [product acceptance](docs/product-acceptance.md) for the release journey and
the distinction between catalog access, actual skill use and routine execution.
