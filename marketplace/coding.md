# Marketplace — Coding

> **Status: Preview.** No loops published yet — the public registry is
> not yet live. The page below shows what this category will look like
> once loops are published.

Feature implementation, refactoring, debugging, code review.

---

## Featured loops

_No loops featured yet. Once the registry is live, this section will
list 0–3 curated loops with a verification badge._

When loops are published, the featured slot will be filled by loops that
meet these criteria:

- ✅ Verified (passes its declared `VERIFY` block against its fixtures).
- Tested on at least two engines.
- Maintained (last commit < 90 days ago).
- Documented (essay + verification + benchmark + replay docs).

---

## New loops

_No loops published yet._

---

## Top contributors

_No contributors yet. Be the first — publish a loop to this category
once the registry is live._

---

## Example loop in this category

The canonical [`coding-loop`](../loops/coding-loop/) loop is a
reference implementation for this category:

Implement features, refactor modules, fix bugs, review PRs — all with verification.

Run it:

```bash
infini install infini/coding-loop@1.0
infini run ./Loopfile.yaml
infini inspect runs/latest/
```

---

## Publishing to this category

Once the registry is live:

1. Write a Loopfile that fits the category.
2. Add `tags: [coding]` to your Loopfile's metadata.
3. Run `infini validate` to confirm spec compliance.
4. Run `infini ci` against fixtures to earn a verification badge.
5. `infini publish` to push to the registry.

Your loop appears in this category within minutes of publish.

---

## Back to marketplace

← [Back to marketplace home](README.md)
