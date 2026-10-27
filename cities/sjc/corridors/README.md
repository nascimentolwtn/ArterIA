# SJC corridor centrelines on the unified network (DRAFT, owner aerial check pending)

Candidates A, C, D, plus a derived B centreline and an A-B connecting route, drawn as
ordered SUMO edge sequences on `cities/sjc/network/sjc.net.xml` (ADR 0016; the net is
gitignored, rebuild with `arteria osm fetch --candidate all` + `arteria network build`).
Edge ids are tied to that build; if the polygons or the OSM snapshot change, rerun.

Files: `corridors.geojson` (one LineString per leg and direction, edge ids in
`properties.edges`), `summary.json` (edges, lengths, street sequence per leg),
`sjc-corridors.kml` (Google Earth: draft study-area polygons + coloured centrelines;
A red, B blue, C orange, D green, A-B link magenta), `corridors-overview.png`,
`build_corridors.py` (regenerates all; needs sumolib), `render_overview.py` (PNG).

## Important: what "same form as B" means here

Corridor B never had an edge-level definition in the repo: it exists only as the
study-area polygon in `study-areas.geojson` (the part the owner aerial-checked). The
polygons are included in the KML (B and C were extended on 2026-10-27, see below). The B centreline here is **derived by
the same method as C, D, A** so the A-B link has real end points; treat it as new and
unchecked.

## Method and assumptions

A leg = waypoints (lon/lat from OSM landmarks) snapped to the nearest passenger edge
(preferring the named streets), joined by least-cost directed paths (cost = length, x8
off the preferred streets, x1.5 for unnamed ramps/connectors). Each leg is routed both
ways; one-way streets and missing turns are therefore respected, and `fwd`/`rev` differ
where the real network does. Lengths are summed edge lengths.

| Leg | Direction | Edges | Length (m) | Reading |
|---|---|---|---|---|
| A anel-viario | fwd (S to N) | 41 | 5314 | Av. Florestan Fernandes -> Av. Senador Teotonio Vilela |
| A anel-viario | rev | 36 | 5462 | same, northern end to southern end |
| D cury-arco-zarur | fwd | 36 | 2351 | Av. Dr. Eduardo Cury -> Arco da Inovacao/Ponte Estaiada junction -> Av. Jorge Zarur (to the Anel interchange) |
| D cury-arco-zarur | rev | 33 | 2103 | |
| D sao-joao-cassiano | fwd | 27 | 2163 | junction -> Av. Sao Joao -> Av. Cassiano Ricardo |
| D sao-joao-cassiano | rev | 36 | 2004 | |
| C sao-dimas-adyana-centro | fwd | 43 | 1900 | Jd. Sao Dimas (Av. Eng. Francisco Jose Longo) -> Vila Adyana -> Praca Afonso Pena |
| C sao-dimas-adyana-centro | rev | 53 | 2366 | |
| B andromeda | fwd / rev | 13 / 10 | 940 / 895 | Av. Andromeda from Jd. Satelite (-23.228) to its north end near the Dutra |
| B andromeda-to-dcta | fwd | 31 | 2499 | Andromeda -> Dutra (about 709 m on the highway) -> Av. Marechal Teixeira Lott -> R. Paraibuna -> Praca Mal.-do-Ar Eduardo Gomes (DCTA gate area) |
| B andromeda-to-dcta | rev | 49 | 2558 | DCTA -> R. Paraibuna/Cacapava/Jambeiro/Acacias/Dinamarca/Romenia ... Viaduto Talim -> Av. Cidade Jardim -> Andromeda (the viaduct loop) |
| C vicentina-rio-branco-loop | fwd | 17 | 1750 | Parque Vicentina Aranha -> Av. Barao do Rio Branco -> R. Madre Paula de Sao Jose -> R. Jose Francisco Alves (extension, 2026-10-27) |
| C vicentina-rio-branco-loop | rev | 33 | 2930 | same, reverse; wanders through R. Augusto Edson Ehlke / Carlos de Campos / Av. Sao Joao (the one-way loop structure) |
| B satelite-perseu | fwd / rev | 26 / 25 | 899 / 874 | Av. Perseu, Jd. Satelite, south to north (extension, 2026-10-27) |
| B satelite-cassiopeia | fwd / rev | 22 / 23 | 758 / 750 | Av. Cassiopeia, Jd. Satelite, east-west (extension, 2026-10-27) |
| **A-B link** | A to B | 14 | 883 | Av. Jorge Zarur (Dutra/Florestan interchange, A) -> R. Antonio Joaquim de Alvarenga -> Av. Cidade Jardim -> R. Jose Alves dos Santos (Andromeda) |
| **A-B link** | B to A | 18 | 1286 | Andromeda -> Av. Cidade Jardim -> Av. Dr. Sebastiao Henrique da Cunha Pontes -> Av. Dep. Benedito Matarazzo (to A) |

The link's edges: A to B `910567309#0 ... 1485678942#7, -329309717#7`; B to A
`329309717#7 ... 772030606#4` (full lists in `summary.json`).

## 2026-10-27 polygon extensions (owner feedback)

- **C** was extended to Parque Vicentina Aranha, Av. Rio Branco, R. Madre Paula de Sao Jose and
  R. Jose Francisco Alves (1.54 to 4.17 km2). All four geocode in Vila Adyana / Jd. Esplanada /
  Vila Ema, i.e. **west and south-west** of the old C polygon, not north; the owner should confirm.
- **B** was extended south through Jd. Satelite along Av. Cassiopeia and Av. Perseu (5.31 to
  7.67 km2, south edge -23.2298 to -23.2381).
- The unified net was rebuilt for the larger envelope: 14,225 edges, 6,655 junctions, 93.1% of
  junctions in the main component, 0 validation errors (ADR 0016's earlier envelope: 11,035 edges).
  Edge ids changed with the rebuild; A, D, B-Andromeda and the A-B link re-routed with identical
  lengths and edge counts. PNG regenerated with a scratchpad venv (matplotlib, sumolib, pyproj).

## Connectivity findings

- A and B are connected in both directions (883 m / 1286 m); no dead end found. The
  asymmetry (B to A is 400 m longer) comes from one-way ramps near the interchange.
- B's detour is visible in the net: A->DCTA-side routing goes through the Dutra
  (709 m) one way and through the Viaduto Talim loop the other way, matching
  `candidate-corridors.md`. This is a result of the OSM geometry, not yet verified on aerials.
- No fwd/rev leg was unroutable.

## Ambiguities (most defensible reading chosen)

- **C** is an area (a one-way maze), not a line; drawn as a spine Sao Dimas -> Vila
  Adyana -> Praca Afonso Pena. The reverse route wandering west (Praca Rotary, Av. Sao
  Joao) is the maze itself. "Sao Dimas" taken as Jd. Sao Dimas (about -23.200).
- **D** is a junction; drawn as the through axis Cury -> Zarur plus the Sao Joao/Cassiano
  Ricardo arm. The junction waypoint snaps onto one of several grade-separated edges, so
  legs include short loops/stubs on the ramps and one stub of Av. Sao Joao NE of the
  junction. The Ponte Estaiada itself appears as "Ponte Pastor Paulo Leivas Macalao".
- **DCTA** has no road node; its gate area (Praca Marechal-do-Ar Eduardo Gomes) is used.
- **A** is Florestan Fernandes + Senador Teotonio Vilela only (the access roads in the
  study-area description are not drawn); the polygon extends beyond the drawn line.
- B's Andromeda spine stops at Jd. Satelite (-23.228); the Perseu/Cassiopeia legs cover the southern extension.
