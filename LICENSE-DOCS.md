# License for documentation and non-code content

Everything under `docs/` (research brief, ADRs, roadmap, thesis tracks), the
`README.md`/`README-eng.md` pair, `CHANGELOG.md`, and any derived/aggregated
data published under `results/published/` are licensed under the **Creative
Commons Attribution 4.0 International License (CC BY 4.0)**.

- Human-readable summary: https://creativecommons.org/licenses/by/4.0/
- Full legal code: https://creativecommons.org/licenses/by/4.0/legalcode

This covers writing and published results, not source code: the `arteria/`
package, its CLI, and tests are licensed separately under Apache License 2.0
(see `LICENSE`).

This does not change how any single data source in a city's
`data-manifest.yaml` is handled — a source marked `visibility: restricted`
(ADR 0003) is never committed or republished here regardless of this
project's own license, because that restriction comes from the data
provider's terms, not from ArterIA.
