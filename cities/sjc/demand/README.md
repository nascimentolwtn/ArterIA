# SJC traffic analysis zones (TAZ, roadmap P3.1, ADR 0017)

One TAZ per enabled study-area candidate (`cities/sjc/study-areas.geojson`,
already aerial-verified per CHANGELOG [1.1]) plus a catch-all `external` zone
for every edge outside all four polygons. Built by
`arteria/demand/zoning.py` (`assign_edges_to_zones`/`build_taz_file`),
exposed as `arteria demand taz --city sjc`, which assigns each network edge
to the zone containing its midpoint (or `external`) and writes a SUMO
`.taz.xml`.

`sjc.taz.xml` itself is gitignored (`cities/*/demand/*.taz.xml`), like the
net it's derived from — it is fully reproducible from the committed
`study-areas.geojson` plus `cities/sjc/network/sjc.net.xml` (itself
reproducible via `arteria network rebuild --city sjc`).

## Real run (2026-10-29, against the net built 2026-10-28, CHANGELOG [1.4])

```
arteria demand taz --city sjc
```

| Zone | Edges |
|---|---|
| a (Anel Viário) | 1,146 |
| b (Av. Andrômeda <-> DCTA / Jardim Satélite) | 3,020 |
| c (Centro / São Dimas / Vila Adyana) | 1,786 |
| d (Jardim Colinas / Ponte Estaiada) | 1,103 |
| external | 7,170 |
| **Total** | 14,225 |

Matches the unified network's known edge count (14,225, ADR 0016); no zone
is empty.

## Next step (not done yet)

This is zoning only (P3.1); the TAZ file carries no production/attraction
weights. P3.2 (OD matrix via a gravity model) needs real population data
(IBGE Censo 2022, per ADR 0017, `Proposed`) joined to these zones before an
OD matrix can be built — tracked in `.claude/napkin.md`.
