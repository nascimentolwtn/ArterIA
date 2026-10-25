# SJC candidate corridors (roadmap P1.3 problem statements / P1.4 study area)

Proposed by the project owner from direct local experience driving these
areas — not yet backed by counts or OD data (those stay `deferred` in
`data-manifest.yaml`). This is the P1.5 problem-statement groundwork, not
the final P1.3 scoring matrix: real scoring needs data this session doesn't
have yet. None of the three is selected as the Phase 1 pilot corridor —
that decision belongs to the owner (see `.claude/napkin.md`, User
Directives: "scope stays SJC-only... the owner decides").

Street names are kept in Portuguese as given; everything else follows
`CLAUDE.md`'s English convention for project docs.

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

## Unconfirmed — elevated bypass underused at a roundabout

**Observed phenomenon, as reported:** a landmark elevated route built over
an at-grade roundabout + traffic light, seemingly designed to remove the
need for the signal entirely. In practice, at peak hours most traffic uses
the roundabout and signal while the elevated route runs free — a "postcard"
structure nobody uses operationally.

**What I found, unconfirmed:** a web search for "bolinho caipira" turned up
nothing tying that name to a specific structure — it came back as a
regional snack food, with no roundabout/viaduct connection in any source.
But I found what may be the actual location: the **Jardim Colinas
roundabout**, where the city's own materials describe a cable-stayed bridge
("Ponte Estaiada" / Arco da Inovação) with two viaducts — upper and lower,
in an X shape — built over that junction. That matches the shape of what
you're describing, but I can't confirm it's the same spot. **Please confirm
the street/location** before this goes further.

**Why it matters if confirmed:** unlike A–C, this isn't a topology problem
(one-way/connector) — the capacity already exists. It would be an
operational question: signal timing biased toward the surface route,
missing/unclear signage, or driver habit/wayfinding. Still squarely in
ArterIA's catalog (P5.2 "signal retiming and transit signal priority") and
RQ1, just a different intervention type than A–C.

## Qualitative first-pass read (not the P1.3 scoring matrix — no counts exist yet)

| Candidate | Peak congestion (reported) | Commute flow | Bus corridor | Bike/ped demand | Lane-realloc feasibility | Data today |
|---|---|---|---|---|---|---|
| A — Anel Viário | Spikes on Dutra incidents | Unknown | Unknown | Unknown | Likely low (wide arterial) | None (OD/counts deferred) |
| B — Andrômeda↔DCTA | Not congestion — forced detour length | Unknown | Unknown | Unknown | Unknown (needs field check) | None |
| C — Centro/São Dimas/Vila Adyana | Not congestion — forced detour length | Likely high (central, commercial) | Possible | Possible | Likely high (narrow streets) | None |

## My read

- **Candidate C** is the cheapest to validate and best demonstrates
  ArterIA's actual pitch (searching one-way/turn-restriction changes against
  a baseline) with the least land-acquisition risk and a compact,
  well-bounded area. Good first target to prototype `network build`/
  `validate` against, even before OD/count data arrives.
- **Candidate B** is structurally the most interesting (a short trip turned
  into a long detour by missing connectivity) but its polygon would need to
  reach into Candidate A's southern Anel Viário segment anyway — consider
  merging B and A into one "DCTA access" study area rather than treating A
  as its own pilot.
- **Candidate A alone** is probably too large/arterial for a first
  microsimulation pilot (brief's buffer-size risk, P1 "Risks"); better
  framed as buffer/boundary context for B.
- This is not a decision, just a recommendation — P1.3's real scoring still
  needs commute/congestion data that's currently deferred, or an
  OSM-only fallback with travel-time proxies (roadmap P1 risk mitigation).

## Open items

1. Confirm the exact street/location of the elevated-bypass phenomenon.
2. Decide whether B's polygon subsumes A's southern segment, or keep them
   as separate study areas sharing a buffer.
3. All three stay provisional until either OD/count data is requested
   (still deferred by the owner's choice, `cities/sjc/data-requests.md`) or
   an open-data-only fallback (OSM + travel-time proxies) is adopted for
   P1.4's study-area polygon.
