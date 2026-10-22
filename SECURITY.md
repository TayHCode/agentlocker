# Security

## Scope and reporting

The self-hosted source preview is available from the project website. This is
an early preview, not a general availability or managed multi-user service.
See the [release guide](docs/release.md) for evidence and limitations.

Report suspected vulnerabilities through the private email contact on
[the security page](https://agentlocker.dev/security.html). The project owner
monitors that address. Include the source revision, affected component and nonsecret reproduction steps.
Keep credentials, private catalog contents, account identifiers and raw client
configuration out of reports and public issues.

The forwarding destination remains private. Do not post vulnerability details
in public issues or assume GitHub private vulnerability reporting is enabled.

## Containment and recovery

If a local catalog connection is implicated, close affected client sessions
and stop the owned catalog process. Back up client configuration privately,
then remove only its `agentlocker` entry (and `agentlocker-gateway` if used),
preserving other settings. If an imported item is implicated, review it and
use `python3 hub.py remove <kind> <name>` with confirmation to remove the owned
import. Removing an item or a client entry does not revoke a provider token.

If credentials may have been exposed, use the provider's approved private
revocation flow. Never send secret values in chat. Preserve evidence privately
and follow the [private-state recovery guidance](docs/release.md#private-state-upgrade-and-rollback)
before restoring anything over live state.

The stdio catalog is read-only and does not resolve `secret://` references.
Executing imported instructions, enabling routines, using the gateway and
authorizing upstream providers require separate review. A clean current-tree
scan does not sanitize historical Git objects. Repository or history-bearing
distribution remains blocked on history review. A source-only archive must be
reviewed for its own contents, exclude private state and evidence, and receive
publication approval.
