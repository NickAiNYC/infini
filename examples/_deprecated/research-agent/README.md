# Research Agent — Golden Example

> Research → Revise → Verify loop. The canonical INFINI demo.

## What this demonstrates

- **DAG execution** with `depends_on`
- **Two-tier verification** (syntactic + semantic)
- **Budget enforcement** ($6 / 20m cap)
- **Memory persistence** (lessons stored for future runs)
- **MCP tools** (browser for web research)

## Run it

```bash
infini validate examples/research-agent/Loopfile.yaml
infini run examples/research-agent/Loopfile.yaml --mock
infini inspect runs/latest/
```

## Loop flow

```
find_sources → extract_claims → verify_citations → write_brief
                                                    ↓
                                              VERIFY (syntactic + semantic)
                                                    ↓
                                              verified or retry (up to 3x)
```
