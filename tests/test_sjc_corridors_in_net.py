"""Desk-only: every corridor edge id exists in the built SJC network.

Skipped where the generated (gitignored) `cities/sjc/network/sjc.net.xml` is absent.
Edge ids are tied to the OSM snapshot (ADR 0016); a failure means the corridors
need re-drawing with `cities/sjc/corridors/build_corridors.py`.
"""

import json
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

SJC = Path(__file__).resolve().parents[1] / "cities" / "sjc"
NET = SJC / "network" / "sjc.net.xml"
CORRIDORS = SJC / "corridors" / "corridors.geojson"


@pytest.mark.skipif(not NET.exists(), reason="built SJC network not present (desk-only)")
def test_every_corridor_edge_exists_in_the_built_network():
    net_edges = {el.get("id") for _, el in ET.iterparse(NET, events=("start",)) if el.tag == "edge"}
    features = json.loads(CORRIDORS.read_text(encoding="utf-8"))["features"]
    missing = {
        (f["properties"]["corridor"], f["properties"]["leg"], f["properties"]["direction"]): [
            e for e in f["properties"]["edges"] if e not in net_edges
        ]
        for f in features
    }
    missing = {k: v for k, v in missing.items() if v}
    assert features
    assert not missing, f"corridor edges absent from {NET.name}: {missing}"
