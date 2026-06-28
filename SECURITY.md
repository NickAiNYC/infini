# Security Policy

## Supported versions

INFINI is pre-1.0. Only the latest minor release receives security fixes.

| Version | Supported |
| ------- | :-------: |
| 1.0.x   |    ✅     |
| < 1.0   |    ❌     |

Once 1.0 ships, the policy becomes: latest minor + the previous minor for 90 days after the next minor releases.

## Reporting a vulnerability

**Do not open a public issue for security disclosures.**

Email **security@infini.dev** (once the domain is live) with:

1. A description of the issue and its impact.
2. A minimal reproduction. A Loopfile + the `infini` command you ran is ideal.
3. Any mitigations you've already tried.
4. Whether you intend to publish a write-up, and if so, when.

You will receive an acknowledgement within 72 hours. We will work with you on a fix and a coordinated disclosure date. We credit reporters in the release notes unless they prefer to remain anonymous.

Until `security@infini.dev` is live, send disclosures via GitHub's private vulnerability reporting at:
**https://github.com/NickAiNYC/infini/security/advisories/new**

## Scope

In scope:

- The Loopfile parser (`infini validate`, `infini run`).
- The trace emitter (`infini inspect`, `run.json`).
- The registry client (`infini install`, `infini publish`) — signature verification, content addressing.
- Engine adapters shipped in this repo (`adapters/hermes/`, `adapters/openclaw/`).
- The INFINI CI GitHub Action.

Out of scope:

- Bugs in third-party engines (LangGraph, CrewAI, AutoGen, etc.). Report those to the engine's maintainers.
- Bugs in models. INFINI is model-agnostic.
- Loopfiles that produce incorrect outputs but pass their declared `VERIFY` block — that's a loop-design problem, not a security problem. (Though if you find a verifier that always returns "pass", that *is* a security problem and we want to know.)

## Signing

The INFINI Reference Engine releases are signed. The public key is in a planned `assets/release-signing.pub`. Verify releases before installing in production.

Loopfiles published to the registry are signed by their publishers, not by INFINI. INFINI does not endorse specific Loopfiles; the registry only verifies that a Loopfile was published by the namespace owner and has not been modified.

## Disclosure timeline

- **Day 0:** Reporter discloses privately.
- **Day 0–3:** Maintainers acknowledge and triage.
- **Day 3–14:** Maintainers and reporter agree on impact, fix, and disclosure date.
- **Day 14–90:** Fix is developed and reviewed privately.
- **Disclosure date:** Coordinated release of fix and public advisory. Credit to reporter.

We will not delay disclosure past 90 days from initial report unless the reporter requests it.

## History

No security advisories have been issued yet. Once they are, they will be listed at https://github.com/NickAiNYC/infini/security/advisories.
