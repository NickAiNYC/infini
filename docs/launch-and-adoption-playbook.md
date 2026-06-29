# INFINI — Launch & Adoption Playbook

> The code is done. The proof is real. Now go get users.

---

## Part 1: The 48-Hour Launch Blitz

### 1.1 The Hacker News Launch Post

**Title:** Show HN: INFINI – Semantic verification for portable agent workflows

**Body:**

I built a portable format for agent workflows called INFINI. The same declarative Loopfile (YAML) runs on multiple engines — the INFINI reference engine and LangGraph — producing identical verified outcomes.

The key innovation is the VERIFY block. It separates:
- Syntactic verification (schema, files, citations)
- Semantic verification (source quality, answer quality, citation accuracy)

The semantic judge scores output 0-100. If confidence is below threshold, the agent retries. In mock mode (deterministic, no API key needed), we see the agent fail at 71.7 confidence on iteration 1, then pass at 91.3 on iteration 2. The mock scores are computed from output quality (length, structure, key terms), not hardcoded.

The portability proof: same Loopfile → reference engine + LangGraph → both verified, same trace format.

Demo: https://asciinema.org/a/f0AuaBa237gzdT2K

Repo: https://github.com/NickAiNYC/infini

```bash
pip install infini-cli
infini run examples/golden-research-assistant/research-loop.yaml --mock
```

What would make you adopt a standard like this? What's the dealbreaker?

**First comment:**
Link to the repo: https://github.com/NickAiNYC/infini
The side-by-side demo script: `bash scripts/demo-side-by-side.sh`

---

### 1.2 The X/Twitter Launch Thread

**Tweet 1:**
2013: Docker standardized containers.
2015: OpenAPI standardized APIs.
2026: LLMs still have no workflow standard.

We built semantic verification for portable agent loops.
The judge failed. The agent retried. It passed.

That's INFINI. 🧵

**Tweet 2:**
Same Loopfile. Reference Engine + LangGraph.

Both produced the same outcome: ✅ verified.

Iteration 1: ❌ 71.7 confidence — failed
Iteration 2: ✅ 91.3 confidence — passed

The agent improved based on semantic feedback.

Demo: https://asciinema.org/a/f0AuaBa237gzdT2K

**Tweet 3:**
Here's how agent frameworks handle workflows today:

| Framework | Portable? | Replayable? | Verifiable? |
|-----------|-----------|-------------|-------------|
| LangGraph | ❌ | ⚠️ | ❌ |
| CrewAI | ❌ | ❌ | ❌ |
| AutoGen | ❌ | ❌ | ❌ |
| INFINI | ✅ | ✅ | ✅ |

Same Loopfile. Any engine. Same trace.

**Tweet 4:**
The 3-agent supervision pattern:
Planner → Worker → Inspector

Hermes plans. OpenClaw executes. Hermes reviews.
It's a single Loopfile. Runs on any engine.

We also shipped the Anthropic 3-agent harness (Plan→Build→Test→Reject→Repair→Improve) as a Loopfile — with the "premature victory" bug fix built into the VERIFY block.

**Tweet 5:**
Try it in 60 seconds:
```bash
pip install infini-cli
infini run examples/golden-research-assistant/research-loop.yaml --mock
```

Repo: https://github.com/NickAiNYC/infini

Same Loopfile. Two engines. Verified. Semantic scores. Real confidence.

**Tweet 6:**
@NousResearch — Hermes could read Loopfiles natively with one PR.
@LangChainAI — LangGraph already supports Loopfiles via our adapter.
@CrewAI — your users want portable workflows.
@Vercel — AI SDK could ship Loopfile support.

The SDK is ready. The spec is stable. Conformance: 8/8.

**Tweet 7:**
INFINI is the OpenTelemetry for agent loops.

Traces first. Portability second. Lock-in never.

Write once. Run anywhere. Debug everywhere.

https://github.com/NickAiNYC/infini

---

### 1.3 The LinkedIn Post

I just shipped an open standard for portable AI agent workflows.

The problem: every agent framework (LangGraph, CrewAI, AutoGen) reinvents orchestration in incompatible ways. Switching frameworks means rewriting everything. Traces are non-portable. Verification is an afterthought.

The solution: INFINI — a declarative Loopfile format that runs on any engine. The same YAML produces identical verified traces across runtimes.

What's working today:
- `pip install infini-cli` — published on PyPI
- Semantic verification with retry loops (agent fails at 71.7 confidence, retries, passes at 91.3)
- LangGraph adapter — same Loopfile runs on two engines
- Time-travel replay — debug any step
- 11 installable loops in the registry, including the Anthropic 3-agent harness

What's honest:
- Mock mode is deterministic (no API key needed)
- Live mode works with Anthropic/OpenAI
- Only 1 contributor (me) — looking for the first external adapter

If you're building agents and tired of framework lock-in, take a look.

Demo: https://asciinema.org/a/f0AuaBa237gzdT2K
Repo: https://github.com/NickAiNYC/infini

#AI #OpenSource #AgentFrameworks #DeveloperTools #Standards

---

### 1.4 The Reddit Posts

**r/LocalLLaMA:**

Title: I built a portable format for agent workflows — same YAML runs on multiple engines with verification

Body:
Tired of rewriting agent workflows when switching frameworks? I built INFINI — a declarative Loopfile that runs on the INFINI reference engine AND LangGraph, producing identical verified traces.

The VERIFY block is the key: syntactic checks (files exist, tests pass) + semantic checks (quality scores 0-100). If confidence is below threshold, the agent retries. Mock mode is deterministic — no API key needed.

```bash
pip install infini-cli
infini run examples/golden-research-assistant/research-loop.yaml --mock
```

Demo: https://asciinema.org/a/f0AuaBa237gzdT2K
Repo: https://github.com/NickAiNYC/infini

**r/AI_Agents:**

Title: Show & Tell: INFINI — semantic verification + portability for agent loops

Body:
Just shipped INFINI — an open standard for portable agent workflows.

Key features:
- Declarative Loopfile (YAML) — runs on any engine
- Semantic verification with retry loops
- Time-travel replay debugging
- LangGraph adapter (same Loopfile, two engines, same trace)
- Anthropic 3-agent harness as a Loopfile
- 11 loops in the registry

The portability proof: same Loopfile → reference engine + LangGraph → both verified.

```bash
pip install infini-cli
infini run examples/golden-research-assistant/research-loop.yaml --mock
```

Demo: https://asciinema.org/a/f0AuaBa237gzdT2K

Looking for feedback and contributors (especially adapter builders for CrewAI, AutoGen, Mastra).

---

### 1.5 The Launch Emails

**To engineers who complained about lock-in:**

Subject: I saw your post about agent framework lock-in

Hi [name],

I saw your post about [specific problem they mentioned]. I've been working on something that tries to solve exactly that — a portable format for agent workflows that runs on any framework.

The project is INFINI (github.com/NickAiNYC/infini). The core idea is a declarative Loopfile that works on LangGraph, the INFINI reference engine, and (soon) CrewAI.

The portability proof is real: the same Loopfile produces identical traces on both the reference engine and LangGraph. Both verified.

Would you be willing to try it and tell me what's wrong with it? I'm looking for honest criticism, not praise.

The quickstart is 60 seconds:
```bash
pip install infini-cli
infini run examples/golden-research-assistant/research-loop.yaml --mock
```

Demo: https://asciinema.org/a/f0AuaBa237gzdT2K

If you have 20 minutes, I'd love to hear your feedback.

Best,
Nick

**To open-source maintainers:**

Subject: Loopfile adapter for [their project] — would you be interested?

Hi [name],

I'm building INFINI — an open standard for portable agent workflows. We have adapters for LangGraph, Hermes, and OpenClaw. I'd love to add [their project].

The adapter is ~300 lines of Python. We have a minimal-adapter template and a conformance suite. If you're interested, I can write the initial PR.

Repo: https://github.com/NickAiNYC/infini
SDK: https://github.com/NickAiNYC/infini/tree/main/sdk

Let me know if this is something you'd consider.

Best,
Nick

**To AI infrastructure VCs:**

Subject: The OpenTelemetry for agent loops — open standard, working proof

Hi [name],

I've been building INFINI — an open standard for portable AI agent workflows. Think Dockerfile for agents, but with built-in semantic verification and time-travel replay.

What's working:
- PyPI package (pip install infini-cli)
- LangGraph adapter (same Loopfile, two engines, identical traces)
- Anthropic 3-agent harness as a Loopfile
- 11 loops in the registry
- 25 tests, 8 conformance tests passing

The bet: engines will keep multiplying. Whoever owns the portable format owns the category. INFINI is the first project to demonstrate actual cross-framework portability.

Repo: https://github.com/NickAiNYC/infini
Demo: https://asciinema.org/a/f0AuaBa237gzdT2K

Would love to chat about the space.

Best,
Nick

---

## Part 2: The 30-Day Adoption Engine

### 2.1 The "Contributor Onboarding" Playbook

**Good First Issues (create these on GitHub):**

1. `good-first-issue` — Add type hints to `cli/src/infini/mock.py`
2. `good-first-issue` — Write a Loopfile for a customer support agent
3. `good-first-issue` — Add `infini task show <id>` command
4. `good-first-issue` — Write tests for `cli/src/infini/memory.py`
5. `good-first-issue` — Add a `--json` output flag to `infini validate`
6. `good-first-issue` — Write a Loopfile for a code review agent
7. `good-first-issue` — Add `infini registry search --json` output
8. `good-first-issue` — Improve error messages in `cli/src/infini/parse.py`
9. `good-first-issue` — Write a tutorial: "Your first Loopfile in 5 minutes"
10. `good-first-issue` — Add `--format` option to `infini inspect`

**Onboarding flow:**

```bash
git clone https://github.com/NickAiNYC/infini
cd infini
python -m venv venv && source venv/bin/activate
pip install -e './cli[dev]'
infini setup
infini conformance tests/conformance/ --mock  # verify everything works
python -m pytest cli/tests/ -q                 # verify tests pass
# Pick a good-first-issue
# Make changes
# Run: python -m pytest cli/tests/ -q
# PR with: closes #<issue-number>
```

**Recognition system:**
- First PR merged → shoutout in CHANGELOG + CONTRIBUTORS.md
- First adapter shipped → "Adapter Maintainer" badge in README
- 5+ PRs merged → "Core Contributor" role in Discord
- First external Loopfile published → "Loop Author" badge

### 2.2 The "Loop Registry" Growth Playbook

**Seed strategy (already done):**
- 10 `@infini/*` canonical loops (hello-world through seo-optimizer)
- 1 `@anthropic/3-agent-harness` flagship loop
- Target: 25 loops by Day 15

**"Loop of the Week" program:**
- Every Monday, highlight one community loop on the README
- Tweet the featured loop with a demo
- The author gets a "Featured" badge in the registry

**"Portability Pledge":**
- Ask 10 open-source agent projects to commit to Loopfile support
- List them in the README under "Portability Pledge Signatories"
- Each signatory gets a badge for their README

**Publisher incentives:**
- Bronze: Listed in registry
- Silver: "Verified" badge
- Gold: "Certified" badge + featured in docs
- Platinum: Homepage feature + co-marketing

### 2.3 The "Adapter Bounty" Program

**Total pool: $10,000**

| Tier | Requirement | Bounty |
|------|-------------|--------|
| Bronze | Parses Loopfiles | $500 |
| Silver | 80% conformance + 1 example | $1,000 |
| Gold | 100% conformance + 3 examples | $2,000 |
| Platinum | Merged into target framework's repo | $5,000 |

**Target frameworks:**
1. CrewAI (highest priority — 40k+ stars)
2. AutoGen (30k+ stars)
3. Mastra (TypeScript ecosystem)
4. OpenAI Agents SDK
5. Google ADK

**Promotion:**
- Tweet the bounty program with prize amounts
- Post in r/AI_Agents, r/LocalLLaMA
- DM maintainers of target frameworks
- Create a `bounty` label on GitHub issues

### 2.4 The "Conformance Week" Hackathon

**Day 1:** "Build your first adapter" — live stream using the SDK
**Day 2:** "Loopfile Gallery" — build and publish loops
**Day 3:** "Verification Challenge" — hardest VERIFY blocks
**Day 4:** "Replay Debugging" — find bugs with time-travel
**Day 5:** "Cross-engine diff" — run on 2+ engines, diff traces
**Day 6:** "MCP Integration" — connect MCP tools to Loopfiles
**Day 7:** "Show & Tell" — demos + prizes

**Prizes:**
- Best adapter: $500
- Best loop: $200
- Best demo: $200
- Most creative use of VERIFY: $100

### 2.5 The Content Engine

**Week 1:**
- Blog: "Why Agent Workflows Need a Standard" (the problem)
- Tutorial: "Your First Loopfile in 5 Minutes"
- Video: "INFINI in 60 Seconds" (the asciinema demo)

**Week 2:**
- Blog: "How INFINI's Semantic Verification Works"
- Tutorial: "Running the Same Loopfile on Two Engines"
- Case study: "The Anthropic 3-Agent Harness as a Loopfile"

**Week 3:**
- Blog: "Time-Travel Replay for Agent Debugging"
- Tutorial: "Building an Adapter with the SDK"
- Comparison: "INFINI vs. LangGraph vs. CrewAI: A Technical Comparison"

**Week 4:**
- Blog: "The Loop Registry: Docker Hub for Agent Loops"
- Tutorial: "Publishing Your First Loop"
- Roadmap: "What's Next for INFINI"

---

## Part 3: The 90-Day Growth Flywheel

### 3.1 The Integration Strategy

**LangGraph (Month 1):**
- Already have the adapter
- Submit PR to LangChain repo: `langgraph_loop_adapter.py`
- DM Harrison Chase: "LangGraph already supports Loopfiles via our adapter. Want to make it official?"

**CrewAI (Month 2):**
- Build the adapter using the bounty program
- DM Joao Moura: "Your users want portable workflows. We have a 300-line adapter ready."

**Hermes (Month 1):**
- File the issue: "Feature Request: `hermes judge` subcommand"
- Submit PR: `hermes loop validate/run/list` commands
- DM maintainer: "205k users could get portable workflows natively."

**MCP (Month 2):**
- Already have MCP tool support in the spec
- Write a tutorial: "Using MCP Servers in Loopfiles"
- Submit to the MCP examples repo

### 3.2 The "OpenTelemetry for Agents" Positioning

**Tagline:** "OpenTelemetry for agent loops. Traces first. Portability second. Lock-in never."

**Elevator pitch:** "INFINI is the portability and verification layer for agent ecosystems. It does not replace LangGraph, CrewAI, or Hermes. It gives them a portable loop contract, trace format, and conformance layer. Write once. Run anywhere. Debug everywhere."

**README hero update:**
Replace "Docker for agents" with "OpenTelemetry for agent loops" in the primary positioning. Docker invites runtime comparisons. OpenTelemetry invites standardization comparisons — which is the right frame.

### 3.3 The "Adopted By" Badge Program

**"Adapter in a Day" challenge:**
- Offer to write the initial adapter PR for any framework
- "Give us 1 hour of your time. We'll write the adapter. You review."
- Target: 5 frameworks in 30 days

**"We'll write the PR for you" offer:**
- For any framework with >10k GitHub stars
- INFINI team writes the adapter
- Framework team reviews and merges
- Both sides get co-marketing

**Co-marketing package:**
- Joint blog post: "Framework X now supports portable Loopfiles"
- Joint tweet: both accounts post
- Badge on both repos: "INFINI Compatible"

### 3.4 The Governance Transition

**Month 1 (now):** Solo maintainer. All decisions by Nick.
**Month 2:** First external contributors. Add to CODEOWNERS for their areas.
**Month 3:** Form TSC (Technical Steering Committee) — 3-5 people.
- Invite: 1 from LangChain, 1 from CrewAI, 1 independent, Nick, 1 more
**Month 4:** Apply to CNCF sandbox (requires: 2 contributors from 2 orgs, clear scope, Apache 2 license)
**Month 6:** CNCF sandbox acceptance → neutral governance

---

## Part 4: The Success Metrics

### 30-Day Milestones

| Metric | Target | How to measure |
|--------|--------|----------------|
| GitHub stars | 500 | GitHub star count |
| PyPI downloads | 2,000 | `pip install infini-cli` downloads |
| External contributors | 5 | GitHub contributors page |
| Loops in registry | 25 | `infini registry search ""` |
| Adapters shipped | 3 | Compatibility matrix |
| HN upvotes | 100 | HN post |
| X impressions | 100,000 | Tweet analytics |
| Discord members | 100 | Discord member count |

### 90-Day Milestones

| Metric | Target | How to measure |
|--------|--------|----------------|
| GitHub stars | 2,000 | GitHub star count |
| PyPI downloads | 20,000 | PyPI stats |
| External contributors | 15 | GitHub contributors page |
| Loops in registry | 100 | Registry count |
| Adapters shipped | 5 | Compatibility matrix |
| Framework integrations | 1 | Official support from 1 framework |
| TSC members | 3 | Governance docs |

### The "Tipping Point" Metrics

INFINI has reached escape velocity when:

1. **A stranger publishes a Loopfile** — someone not in your network publishes to the registry without you asking
2. **A framework maintainer opens an issue** — someone from LangChain/CrewAI opens an issue in your repo (not you in theirs)
3. **A blog post you didn't write** — someone writes about INFINI without you asking
4. **A PR from an unknown contributor** — someone you've never met submits a PR
5. **"INFINI Compatible" appears on another repo's README** — adoption is real when others claim compatibility

When 3 of these 5 have happened, INFINI has escaped. Until then, every day is push day.

---

## The Execution Order

| Day | Action | Time | Outcome |
|-----|--------|------|---------|
| 1 | Post on HN | 30 min | First wave of users |
| 1 | Post X thread | 30 min | Distribution |
| 1 | Post on Reddit (3 subs) | 30 min | Developer audience |
| 1 | Post on LinkedIn | 15 min | Enterprise audience |
| 2 | Email 10 engineers | 2 hours | Direct feedback |
| 2 | Email 5 OSS maintainers | 1 hour | Partnership leads |
| 2 | Email 3 VCs | 30 min | Funding conversations |
| 3 | File Hermes issue | 15 min | Ecosystem signal |
| 3 | Create 10 good-first-issues | 1 hour | Contributor funnel |
| 4-7 | Respond to all comments | Ongoing | Community building |
| 7 | Publish first blog post | 2 hours | SEO + thought leadership |
| 7 | Launch Adapter Bounty | 1 hour | Adapter pipeline |
| 14 | Publish second blog post | 2 hours | Sustained attention |
| 14 | Launch "Loop of the Week" | 30 min | Registry growth |
| 21 | Publish third blog post | 2 hours | Depth |
| 21 | Host Conformance Week hackathon | 7 days | Community event |
| 30 | Publish 30-day retrospective | 2 hours | Transparency + momentum |

---

*"The code is done. The proof is real. The demo is recorded. The playbook is written. Now execute."*
