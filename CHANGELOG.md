# Changelog

## Unreleased

Self-hosted shared skills and routine instructions for local agents and hosted
bots. Claude Code, Codex CLI and Grok Bot have bounded owner-trial evidence for
catalog use and updates; routine execution through controlled local clients is
also recorded. Automatic scheduling remains optional and unverified. No release
tag exists yet. See [evidence and release requirements](docs/release.md).

- Add a repeatable offline proof covering import with supporting files, catalog
  reads, client configuration preservation, update history and removal.
- Record successful model-driven Claude Code and Codex catalog acceptance on
  synthetic imported content using existing product logins.
- Warn when client connection entries point at a linked Git review worktree.
- Document runtime requirements, private-state backup and isolated restoration,
  stable installation, release gates and rollback limits.
- Correct the current audit disposition while retaining the historical audit.
- Configure one self-hosted catalog URL for hosted client instructions, routine
  prompts and optional Composio registration, with validated per-command overrides.
- Require explicit local-content selection before publishing and support an
  installed Wrangler alongside `cf` and the Cloudflare API transport.
- Add `doctor` for installed catalogs without imposing maintainer commit
  identities, and document the first-user self-host setup.

Executor, MCPHub, Composio, agents-sync, the setup wizard and the remote Worker
remain included. Live upstream providers, gateway operation, automatic
schedules, other operating systems and independent-user installation remain
unverified. Hosted catalog evidence is limited to the recorded owner staging
trial. See the [release guide](docs/release.md).
