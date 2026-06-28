# ADRs (Architecture Decision Records)

Formal records of architectural decisions made in INFINI. Each ADR
explains the context, decision, and consequences of a design choice.

| ADR | Title | Status |
| --- | --- | --- |
| [ADR-001](ADR-001-sqlite-not-redis.md) | Use SQLite instead of Redis | Accepted |
| [ADR-002](ADR-002-anthropic-skills-standard.md) | Adopt Anthropic Skills Standard for Plugins | Accepted |
| [ADR-003](ADR-003-verbatim-storage.md) | Verbatim Storage vs. Summarization | Accepted |

## Format

Each ADR follows:

- **Context:** Why this decision was needed
- **Decision:** What was decided
- **Consequences:** What happens as a result (positive and negative)
- **Attribution:** Where the idea came from

## Why ADRs?

ADRs are the ultimate senior engineer signal. They show that
architectural decisions are deliberate, defensible, and documented.
They prevent "why did we do it this way?" conversations months later.

See [Michael Nygard's original article](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)
for the ADR format.
