# INFINI Canonical Loops

The 12 canonical loops are the **Design Patterns book** for agent work. Each is curated, versioned, and benchmarked. Each ships with:

- `Loopfile.yaml` — the loop itself.
- `essay.md` — *why* this loop exists, *when* to use it, *when not* to.
- `fixtures/` — at least one fixture set the loop can be tested against.
- `expected/` — the expected trace shape, for CI.

Install any with `infini install infini/<name>@<version>`.

---

## The 12 loops

| Loop | What it does | Status |
| --- | --- | --- |
| [`coding-loop`](coding-loop/)     | Implement a feature, preserve tests | draft |
| [`refactor-loop`](refactor-loop/) | Refactor a module without behavior change | planned |
| [`test-gen-loop`](test-gen-loop/) | Generate tests until coverage hits target | planned |
| [`debug-loop`](debug-loop/)       | Reproduce, isolate, fix, verify a bug | planned |
| [`review-loop`](review-loop/)     | Code review with rubric + cross-check | planned |
| [`research-loop`](research-loop/) | Multi-source research with citations | planned |
| [`content-loop`](content-loop/)   | Draft → critique → revise content | planned |
| [`outreach-loop`](outreach-loop/) | Personalized outreach at scale | planned |
| [`migration-loop`](migration-loop/) | Migrate code across versions | planned |
| [`doc-sync-loop`](doc-sync-loop/) | Keep docs in sync with code | planned |
| [`oncall-loop`](oncall-loop/)     | Triage incidents, propose fixes | planned |
| [`sre-loop`](sre-loop/)           | Investigate, mitigate, postmortem | planned |

---

## What makes a loop "canonical"

A loop is canonical when:

1. **It's common.** At least three unrelated teams would use it as-is.
2. **It's non-obvious.** The right `VERIFY` and `STOP_WHEN` are not trivially discoverable.
3. **It's portable.** It runs on at least two engines without modification.
4. **It's tested.** It ships with fixtures and an expected trace shape, and `infini ci` passes.

Loops that don't clear this bar belong in [`../examples/`](../examples/), not here.

---

## Contributing a canonical loop

See [`../CONTRIBUTING.md`](../CONTRIBUTING.md#new-canonical-loops). The bar is high. We'd rather have 12 great loops than 50 mediocre ones.

---

## License

MIT. See [repository LICENSE](../LICENSE).
