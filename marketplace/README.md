# INFINI Marketplace

> **Status: Preview.** This is a static mock of the future marketplace UI.
> The real marketplace ships after the public registry launches. No loops
> are listed here yet because the registry is not yet live. When it is,
> the listings below will be populated from real registry data.

The marketplace is a browseable view of the INFINI registry, organized
by use case. It is a UI on top of the registry protocol defined in
[RFC-0005](../spec/rfcs/RFC-0005-registry.md); it adds no new protocol.

---

## Categories

| Category | Description |
| --- | --- |
| [Research](research.md)       | Multi-source research loops with citations. |
| [Coding](coding.md)           | Feature implementation, refactoring, debugging. |
| [Compliance](compliance.md)   | Audit, policy, regulatory workflows. |
| [Security](security.md)       | Vulnerability research, incident response. |
| [Sales](sales.md)             | Outreach, prospecting, account research. |
| [SEO](seo.md)                 | Keyword research, content optimization. |
| [Marketing](marketing.md)     | Content drafting, campaign analysis. |
| [Healthcare](healthcare.md)   | Clinical research, claims audit. |
| [Finance](finance.md)         | Reconciliation, risk analysis, reporting. |
| [Legal](legal.md)             | Contract review, case research. |
| [Education](education.md)     | Lesson planning, assessment, tutoring. |
| [Infrastructure](infrastructure.md) | SRE, oncall, deployment automation. |

---

## What you'll see when the marketplace is live

Each category page shows:

- **Featured loops.** 0–3 curated loops, with a verification badge.
- **New loops.** Recently published in this category.
- **Top contributors.** Publishers with the most verified loops in this
  category.
- **Supported engines.** Which adapters each loop has been tested
  against.

Every loop shows:

- Name, version, publisher, description.
- Verification badge: ✅ Verified, ⚠ Unverified, ❌ No verification.
- Supported engines.
- Estimated runtime, estimated cost.
- Required tools.
- Maintainer, license.
- Real download count (no fake numbers).

---

## Non-negotiable principles

- **No fake featured loops.** Until a real loop is published and
  verified, the featured slot is empty.
- **No fake downloads.** The download count is real, pulled from the
  registry.
- **No paid placement.** The marketplace is neutral. Featured loops are
  curated by maintainers based on verification score and adoption, not
  on payment.
- **Verification over popularity.** A loop with 5 stars and verified ✅
  is featured above a loop with 5000 stars and no verification.

---

## Mock vs. real

The pages in this directory are static markdown mocks. They look like
what the real marketplace will look like, with placeholder text where
real data will go. When the registry ships, this directory will be
replaced by a dynamic site at `marketplace.infini.dev`.

Until then, browse the [12 canonical loops](../loops/) for runnable
examples.

---

## License

CC-BY-4.0. See [repository LICENSE](../LICENSE).
