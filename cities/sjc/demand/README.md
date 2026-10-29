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

## Population by zone (P3.2 production weights, 2026-10-29)

IBGE Censo 2022 population by census tract (`ibge-censo-populacao-setores`
in `cities/sjc/data-manifest.yaml`), joined to these same TAZs by
`arteria/demand/population.py` (`load_setores`/`population_by_zone`), each
setor's centroid assigned to whichever zone polygon contains it.

```
arteria demand population --city sjc --gpkg-path data/SP_setores_CD2022.gpkg --table SP_setores_CD2022
```

| Zone | Population |
|---|---|
| a | 13,499 |
| b | 36,391 |
| c | 24,516 |
| d | 22,702 |
| external | 599,946 |
| **Total** | 697,054 |

1,554 census tracts. The `external` zone dominates because the four study
areas are small, aerial-verified pilot-corridor buffers, not the whole
municipality (SJC's full 2022 population is ~730k).

## Next step (not done yet)

The attraction side of the gravity model (jobs/land-use proxy, per ADR 0017)
is still missing: the Geosanja "03 Macrozoneamento Urbano" zoning layer
named in that ADR was never actually downloaded (only road-hierarchy layers
were — see the `geosanja-plano-diretor-zoneamento` manifest entry), and its
portal isn't scriptable from this session (a guessed GeoServer WFS endpoint
required auth). Getting it needs a desk browser session or the owner
fetching it by hand. The gravity-model OD matrix itself cannot be built
until that's resolved — tracked in `.claude/napkin.md`.
