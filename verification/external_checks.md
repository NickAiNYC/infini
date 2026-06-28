# External Checks

External verification checks the world's response, not the loop's output. These are the canonical check names engines should support.

## Naming convention

`{category}:{assertion}`

Examples:
- `tests:pass`
- `lint:clean`
- `screenshot_diff:<5%`
- `api:200`
- `build:success`
- `coverage:>=80`

## Categories

### `tests`
Runs the project's test suite. Assertions: `pass`, `fail`, `pass_count>=N`.

### `lint`
Runs the linter. Assertions: `clean`, `errors==0`, `warnings<=N`.

### `typecheck`
Runs the type checker. Assertions: `pass`, `errors==0`.

### `build`
Runs the build. Assertions: `success`, `failure`.

### `coverage`
Measures test coverage. Assertions: `>=N`, `>=baseline`.

### `screenshot_diff`
Compares screenshots before/after. Assertions: `<N%`, `unchanged`.

### `api`
Calls an HTTP API. Assertions: `200`, `2xx`, `response_matches:{schema}`.

### `browser`
Runs a browser smoke test. Assertions: `load`, `no_console_errors`, `text_visible:{selector}`.

### `perf`
Measures performance. Assertions: `p95<Nms`, `throughput>=N`.

### `links`
Checks hyperlinks. Assertions: `valid`, `no_dead_links`.

## Custom checks

Engines may support custom checks. They must be documented in the engine's manifest. Loops that use engine-specific checks are marked with the engine name in the registry.

## Failure handling

External check failures count toward the loop's `confidence_threshold`. A single external failure can fail the entire verify stage, depending on the loop's `confidence_threshold` and `STOP_WHEN` configuration.
