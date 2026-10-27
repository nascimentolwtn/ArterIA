# SJC network patches

`manifest.yaml` lists patch files in the order they are applied. Each is plain XML named by kind:
`.nod.xml` (nodes), `.edg.xml` (edges), `.con.xml` (connections), `.tll.xml` (traffic lights).
Edge and node entries with an existing id override attributes of the OSM-built net; `<delete .../>`
removes things. SUMO 1.28 `netconvert` has no `--patch-files`, and edge files given together with
`--osm-files` are read as new edges, so patches run in a second pass over `sjc.base.net.xml`.

Example (`001-slow-service-road.edg.xml`, then list it in the manifest with a reason and evidence):

```xml
<edges><edge id="-1007645596#1" speed="3.00"/></edges>
```

```yaml
patches:
  - file: 001-slow-service-road.edg.xml
    reason: OSM has no maxspeed; field note says 10 km/h
    evidence: aerial imagery 2026-10-27 / OSM way 1007645596
```

After adding a patch, re-pin the reference net: `arteria network rebuild --city sjc --update-snapshot`.
Edge ids on the corridors (`cities/sjc/corridors/`) must still exist: `pytest tests/test_sjc_corridors_in_net.py`.
