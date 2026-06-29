# INFINI Observatory UI

The local Next.js 15 dashboard for visualizing Loopfile execution traces.
The signature feature — the DevTools for autonomous systems.

> **Status: Preview.** The UI renders traces produced by `infini run --mock`.
> Drop a `run.json` file onto the dashboard to visualize any trace in 3D.

---

## Quickstart

```bash
cd observatory-ui
npm install
npm run dev
# open http://localhost:3000
```

Or launch from the CLI:

```bash
infini ui runs/latest/run.json
```

---

## What you'll see

- **3D execution graph** — React Three Fiber renders the loop's steps as an
  interactive 3D node graph. Rotate, zoom, click any node to inspect.
- **Stat cards** — total runs, active sessions, mean replay time, certified
  adapters.
- **Audited log stream** — every step with timestamp, cost, duration.
- **Replay visualization center** — click a node to see its cost, tokens,
  artifacts, and a "Replay from here" button.
- **Verification results** — every check, pass/fail, confidence score.

---

## Aesthetic

Deep charcoal background with atmospheric cyan haze. Soft glowing outlines
around every panel. Clean techno-sans-serif typography. Framer Motion
transitions between states. The goal: look like a premium AI product,
not a cluttered terminal.

---

## Architecture

```
observatory-ui/
├── src/
│   ├── app/
│   │   ├── layout.tsx      # root layout, dark mode
│   │   ├── page.tsx        # the Observatory dashboard
│   │   └── globals.css     # the aesthetic (charcoal + cyan haze)
│   └── components/         # shadcn/ui components
├── package.json
└── README.md               # this file
```

The 3D graph is built with React Three Fiber (`@react-three/fiber`) and
Drei (`@react-three/drei`). The trace format is defined in
[`spec/loopfile-v1.md`](../spec/loopfile-v1.md) §10.

---

## Uploading a trace

Run a loop:

```bash
infini run examples/github-pr-review/coding-loop.yaml --mock
```

This produces `runs/latest/run.json`. Open the Observatory UI and click
**Upload Trace**, or:

```bash
infini ui runs/latest/run.json
```

The 3D graph re-renders with your trace's steps.

---

## License

MIT. See [repository LICENSE](../LICENSE).
