# Architecture

> What the system **is** and where code belongs. Structure truths only — no style preferences (those live in `.claude/rules/`).
> Update in the same PR as any structural change (rule E1).

## Repo layout
| Path | What lives here | Deployable? | Owner |
|------|-----------------|-------------|-------|
| | | | |
| | | | |

## Where data truth lives
<the database, the cache, what is derived, what is authoritative for each entity>

## Boundaries and contracts
| Boundary | Format | Source of truth | Generated output (never hand-edited) | Regeneration command |
|----------|--------|-----------------|--------------------------------------|----------------------|
| | | | | |

## Environments
| Env | URL | Database | Who may touch it |
|-----|-----|----------|------------------|
| local | | | anyone |
| staging | | | team |
| production | | | **not the agent** (rule C5) |

## Key flows
### 1. <e.g. checkout>
<the steps across layers and services, and where it can fail>

## External integrations
| Service | Purpose | Failure mode | Sandbox available? |
|---------|---------|--------------|--------------------|

## Known constraints and landmines
- <the legacy module, the nightly job, the endpoint a client polls>
