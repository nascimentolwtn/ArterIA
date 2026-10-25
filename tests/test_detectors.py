import xml.etree.ElementTree as ET

from arteria.calibration.detectors import CountLocation, build_induction_loops

TOY_NET_XML = """<?xml version="1.0" encoding="UTF-8"?>
<net version="1.20">
    <edge id="A" from="n0" to="n1" priority="1" numLanes="2" speed="13.89">
        <lane id="A_0" index="0" speed="13.89" length="100.00" shape="0,0 100,0"/>
        <lane id="A_1" index="1" speed="13.89" length="120.00" shape="0,3 100,3"/>
    </edge>
    <edge id="B" from="n1" to="n2" priority="1" numLanes="1" speed="13.89">
        <lane id="B_0" index="0" speed="13.89" length="50.00" shape="100,0 150,0"/>
    </edge>
</net>
"""


def test_matched_location_emits_one_detector_per_lane() -> None:
    locations = [CountLocation(count_id="c1", edge_id="A", position_m=50.0)]

    result = build_induction_loops(TOY_NET_XML, locations)

    root = ET.fromstring(result.additional_xml)
    loops = root.findall("inductionLoop")
    assert len(loops) == 2

    by_id = {loop.get("id"): loop for loop in loops}
    assert by_id["c1_A_0"].get("lane") == "A_0"
    assert by_id["c1_A_0"].get("pos") == "50.0"
    assert by_id["c1_A_1"].get("lane") == "A_1"
    assert by_id["c1_A_1"].get("pos") == "50.0"
    for loop in loops:
        assert loop.get("freq") == "3600"
        assert loop.get("file") == "detectors.out.xml"

    assert result.unmatched == []
    assert result.clamped == []


def test_unknown_edge_is_reported_unmatched_and_emits_nothing() -> None:
    locations = [CountLocation(count_id="ghost", edge_id="does-not-exist", position_m=10.0)]

    result = build_induction_loops(TOY_NET_XML, locations)

    root = ET.fromstring(result.additional_xml)
    assert root.findall("inductionLoop") == []
    assert result.unmatched == ["ghost"]
    assert result.clamped == []


def test_out_of_range_position_is_clamped_and_reported_once() -> None:
    # Edge "B" has a single lane of length 50.0; 500.0 is far beyond it.
    locations = [CountLocation(count_id="c2", edge_id="B", position_m=500.0)]

    result = build_induction_loops(TOY_NET_XML, locations)

    root = ET.fromstring(result.additional_xml)
    loops = root.findall("inductionLoop")
    assert len(loops) == 1
    assert loops[0].get("id") == "c2_B_0"
    pos = float(loops[0].get("pos", "nan"))
    assert 0.0 <= pos < 50.0
    assert pos == 49.9

    assert result.clamped == ["c2"]
    assert result.clamped.count("c2") == 1
    assert result.unmatched == []


def test_negative_position_is_clamped_into_range() -> None:
    locations = [CountLocation(count_id="c3", edge_id="B", position_m=-5.0)]

    result = build_induction_loops(TOY_NET_XML, locations)

    loops = ET.fromstring(result.additional_xml).findall("inductionLoop")
    assert len(loops) == 1
    pos = float(loops[0].get("pos", "nan"))
    assert 0.0 <= pos < 50.0
    assert result.clamped == ["c3"]


def test_clamped_count_id_not_duplicated_across_multiple_lanes() -> None:
    # Edge "A" has 2 lanes (lengths 100.0 and 120.0); a position beyond both
    # forces clamping on both lanes but "c4" must appear only once.
    locations = [CountLocation(count_id="c4", edge_id="A", position_m=1000.0)]

    result = build_induction_loops(TOY_NET_XML, locations)

    loops = ET.fromstring(result.additional_xml).findall("inductionLoop")
    assert len(loops) == 2
    assert result.clamped == ["c4"]


def test_additional_xml_round_trips_as_valid_xml() -> None:
    locations = [
        CountLocation(count_id="c1", edge_id="A", position_m=50.0),
        CountLocation(count_id="ghost", edge_id="does-not-exist", position_m=10.0),
        CountLocation(count_id="c2", edge_id="B", position_m=500.0),
    ]

    result = build_induction_loops(TOY_NET_XML, locations)

    root = ET.fromstring(result.additional_xml)
    assert root.tag == "additional"
    # 2 lanes on A + 1 lane on B; "ghost" contributes nothing.
    assert len(root.findall("inductionLoop")) == 3
