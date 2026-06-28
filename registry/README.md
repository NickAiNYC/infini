# INFINI Registry

> Git-based. No hosted service. Adapters live in directories; the
> registry is a structured index.

## Structure

```
registry/
├── official/         ← INFINI team maintained (hermes, openclaw)
├── community/        ← community maintained, certified
├── experimental/     ← community maintained, not yet certified
└── certifications/   ← generated certification reports
```

## Official adapters

| Adapter | Type | Status | Compatibility |
| --- | --- | --- | --- |
| [`hermes`](official/hermes/) | governance | certified | 70.8% |
| [`openclaw`](official/openclaw/) | execution | certified | 66.7% |

## Community adapters

_None yet. Be the first — see the [Adapter SDK](../sdk/) and
[Publishing Guide](../sdk/publishing-guide.md)._

## Experimental adapters

_None yet._

## Publishing an adapter

1. Build an adapter using the [SDK](../sdk/)
2. Get it [certified](../sdk/certification-guide.md)
3. PR to `registry/community/<your-adapter>/` with:
   - `manifest.yaml`
   - `metadata.json`
   - `README.md`
   - `compatibility.json` (from `infini certify`)
   - `examples/` (at least one runnable Loopfile)

See the [Publishing Guide](../sdk/publishing-guide.md) for details.
