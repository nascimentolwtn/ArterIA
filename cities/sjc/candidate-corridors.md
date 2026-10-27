# SJC candidate corridors (roadmap P1.3 problem statements / P1.4 study area)

Proposed by the project owner from direct local experience driving these
areas — not yet backed by counts or OD data (those stay `deferred` in
`data-manifest.yaml`).

Street names are kept in Portuguese as given; everything else follows
`CLAUDE.md`'s English convention for project docs.

## Decision (2026-10-25): all four areas in scope, priority order B > D > C > A

The owner has decided all four candidates below are in scope for SJC, to be
worked in this priority order:

1. **B** — Av. Andrômeda ↔ DCTA / Jardim Satélite
2. **D** — Jardim Colinas roundabout / Ponte Estaiada (confirmed — see
   Candidate D below)
3. **C** — Centro / São Dimas / Vila Adyana one-way maze
4. **A** — Anel Viário and its access roads

This is a qualitative, owner-level priority call, not the data-backed P1.3
scoring matrix (no OD/count data exists yet — see "Qualitative first-pass
read" below). It supersedes the "My read" recommendation further down this
file, which had suggested starting with C for its lower cost/risk; the
owner chose to lead with B instead. Two practical notes on that:

- **B first means tackling a genuine missing-connectivity case before a
  simpler one-way/turn-restriction case.** Fixing it may need a new
  connector edge (catalog P5.2's "new connector edge, only from a
  pre-approved list" — the costliest, most land-constrained intervention
  type) rather than just a turn-restriction relaxation. Worth confirming
  during P5.3 candidate generation whether a connector is even feasible
  there before committing engineering time to it specifically.
- **D second means the transform library (P5.2) needs signal-retiming
  logic earlier than the roadmap currently sequences it** (today's code,
  `turn_restriction.py`, only handles connection removal). That's a
  heads-up for whoever picks up P5.2, not a blocker now.

**Resolved 2026-10-25:** Candidate B's polygon connects to the Anel Viário
(Candidate A) rather than treating them as fully separate study areas — see
Candidate A and Candidate B below.

## Candidate A — Anel Viário and its access roads, Dutra to "fundo do vale"

**Observed phenomenon:** SJC is a medium-sized city without heavy baseline
traffic, except at peak hours or when an incident on the Dutra (BR-116) has
no real alternative route. The Anel Viário (Av. Florestan Fernandes / Av.
Teotônio Vilela) is the de facto bypass, but its own access roads down to
the valley floor are part of the same bottleneck story.

**Research questions addressed:** RQ1 (which corridors benefit from
reversible lanes/one-way conversions/lane reallocation), RQ5 (spillover to
the buffer zone — the Anel Viário *is* the buffer/diversion route when
Dutra fails).

**Feasibility note:** likely a wide-ROW arterial already, so lane
reallocation may be less feasible than on narrower streets (brief's 5th
scoring criterion) — probably better framed as *buffer context* for
Candidate B than as a standalone pilot (see "My read" below).

**Resolved 2026-10-25:** the owner confirmed Candidate B's polygon connects
to A's southern segment rather than treating them as fully separate study
areas (see Candidate B below).

## Candidate B — Av. Andrômeda ↔ DCTA / Jardim Satélite

**Observed phenomenon:** there is no direct link. Westbound from Av.
Andrômeda to DCTA requires either the Dutra, or a long loop through small
viaducts climbing via Bairro São Bento or Vila Letônia. Eastbound from DCTA
toward Jardim Satélite has the same problem in reverse: either the same
viaduct loop, or the Dutra to the Anel Viário, a retorno, then via Av.
Letônia Melin back into Av. Andrômeda. A short trip becomes a long detour
in both directions.

**Research questions addressed:** RQ1, RQ4 (low-cost connectors or turn
restrictions that cut this detour materially).

**Note:** DCTA (Departamento de Ciência e Tecnologia Aeroespacial) is an
aerospace/defense installation. If the `unifa-ppgca` thesis track (Poder
Aeroespacial, Segurança e Defesa) ever wants an access/resilience case
study tied to a real installation, this corridor is a natural fit — but
that's a thesis-scope call for the owner/an advisor, not decided here.

**Polygon, confirmed 2026-10-25:** connects to Candidate A's Anel Viário
segment rather than standing as a fully separate study area, matching the
westbound/eastbound detour description above (the Anel Viário is part of
the eastbound return loop).

**Extended south, 2026-10-27 (owner feedback):** the loop/one-way structure
continues southbound through Jd. Satélite, so B's polygon now also covers
Av. Cassiopéia and Av. Perseu (about 5.3 to 7.7 km2; area grew southward to
about -23.238). Aerial-checked by the owner 2026-10-27, good for now.

**Future extension (optional, not current priority):** the same DCTA ↔
Dutra dependency also exists northbound, toward the Vista Verde
neighborhood — logged here for later consideration, not part of the
current B polygon/build.

## Candidate C — Centro / São Dimas / Vila Adyana one-way maze

**Observed phenomenon:** several consecutive one-way streets running the
"wrong" way for a given turn. You keep driving expecting the next street to
let you turn, and it's one-way again — sometimes two or three blocks in a
row — until you find a street that lets you turn, re-enter the avenue near
your actual destination, or peel off toward another neighborhood entirely.

**Research questions addressed:** RQ1 and RQ4 most directly of the three.
Also the most tractable of the three on the brief's "feasibility of lane
reallocation without major land acquisition" criterion — narrower
residential/commercial streets, no earthworks implied.

**Extended 2026-10-27 (owner feedback):** C's polygon now also covers Parque
Vicentina Aranha, Av. Barão do Rio Branco, R. Madre Paula de São José and
R. José Francisco Alves, where the one-way turn/loop structure continues
(about 1.5 to 4.2 km2). Geocoding places these streets west/south-west of the
original polygon (Vila Adyana / Jd. Esplanada / Vila Ema), not north; the owner
should confirm that is the area meant.

## Candidate D — Jardim Colinas roundabout / Ponte Estaiada

**Confirmed 2026-10-25.** The structure is the **Jardim Colinas
roundabout**, where the city's own materials describe a cable-stayed
bridge ("Ponte Estaiada" / Arco da Inovação) with two viaducts — upper and
lower, in an X shape — built over that junction.

**Observed phenomenon:** a landmark elevated route built over an at-grade
roundabout + traffic light, seemingly designed to remove the need for the
signal entirely. In practice, at peak hours most traffic uses the
roundabout and signal while the elevated route runs free — a "postcard"
structure nobody uses operationally.

**Why it matters:** unlike A–C, this isn't a topology problem
(one-way/connector) — the capacity already exists. It's an operational
question: signal timing biased toward the surface route, missing/unclear
signage, or driver habit/wayfinding. Still squarely in ArterIA's catalog
(P5.2 "signal retiming and transit signal priority") and RQ1, just a
different intervention type than A–C.

## Qualitative first-pass read (not the P1.3 scoring matrix — no counts exist yet)

| Candidate | Peak congestion (reported) | Commute flow | Bus corridor | Bike/ped demand | Lane-realloc feasibility | Data today |
|---|---|---|---|---|---|---|
| A — Anel Viário | Spikes on Dutra incidents | Unknown | Unknown | Unknown | Likely low (wide arterial) | None (OD/counts deferred) |
| B — Andrômeda↔DCTA | Not congestion — forced detour length | Unknown | Unknown | Unknown | Unknown (needs field check) | None |
| C — Centro/São Dimas/Vila Adyana | Not congestion — forced detour length | Likely high (central, commercial) | Possible | Possible | Likely high (narrow streets) | None |
| D — Jardim Colinas roundabout | Reported: underused at peak hours | N/A (operational, not a route choice problem per se) | Possible (bus routes likely cross it) | Unknown | N/A — capacity exists, this is a signal/routing question | None |

## My read (superseded by the owner's decision above — kept for the reasoning)

- **Candidate C** looked cheapest to validate and best demonstrated
  ArterIA's actual pitch (searching one-way/turn-restriction changes against
  a baseline) with the least land-acquisition risk and a compact,
  well-bounded area — my suggested first target to prototype `network
  build`/`validate` against. The owner chose to lead with B instead (see
  "Decision" above); that stands.
- **Candidate B** is structurally the most interesting (a short trip turned
  into a long detour by missing connectivity); its polygon connects to
  Candidate A's southern Anel Viário segment, confirmed by the owner.
- **Candidate A alone** is probably too large/arterial for a first
  microsimulation pilot (brief's buffer-size risk, P1 "Risks"); better
  framed as buffer/boundary context for B when A's turn comes up, 4th in
  priority.
- This was a recommendation, not a decision — P1.3's real scoring still
  needs commute/congestion data that's currently deferred, or an
  OSM-only fallback with travel-time proxies (roadmap P1 risk mitigation).
  The owner's priority order above is itself qualitative for the same
  reason; it isn't expected to wait for that data.

## Open items

1. All four stay provisional on real evidence until either OD/count data
   is requested (still deferred by the owner's choice,
   `cities/sjc/data-requests.md`) or an open-data-only fallback (OSM +
   travel-time proxies) is adopted for each area's P1.4 study-area polygon.
2. **Polygon tooling is ready, the run isn't.** `arteria studyarea build
   --city sjc --user-agent "<yours>"` (roadmap P1.4,
   `arteria/network/study_area.py`) geocodes each candidate's landmark list
   in `cities/sjc/study-areas.yaml` via Nominatim and writes
   `cities/sjc/study-areas.geojson` — one polygon per candidate, buffered
   convex hulls, B's hull already including the Anel Viário landmarks so it
   connects to A as decided. It needs real network access to
   `nominatim.openstreetmap.org`, which this remote session doesn't have
   (ADR 0009); run it at the desk. **Treat the output as a draft** — check
   it against satellite imagery/OSM before using it for a real P2.1
   extraction, same caution the roadmap already gives OSM completeness.
3. The Vista Verde northbound extension to Candidate B is in
   `study-areas.yaml` as a disabled candidate (`b_ext_vista_verde`) — no
   priority, run with `--include-future` if it's ever wanted; it's a future
   option, not current work.
