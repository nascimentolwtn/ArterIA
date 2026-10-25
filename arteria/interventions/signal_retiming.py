"""Signal-retiming transform: phase-duration edit (roadmap P5.2, remote task R18).

A signal-retiming candidate is applied as a deterministic network transform:
set each `<phase duration="...">` on one `<tlLogic>` of a SUMO `.net.xml`
document, identified by its `id`. Like `turn_restriction.py` and
`lane_restriction.py`, this module only edits the plain XML with the
standard-library `xml.etree.ElementTree` -- no `sumolib` and no real
`netconvert`/`sumo` binary, per the remote-session boundary (ADR 0009). The
real build and a field-timing comparison stay at the desk; this operates on
hand-written toy fixtures.

This transform only changes phase *durations*, in the existing phase order.
It does not add, remove or reorder phases, and it does not touch `state`
(signal indication) strings -- retiming a cycle is a different catalog entry
from redesigning its phase structure, and the latter is out of scope here.
Transit signal priority (holding/extending a phase for an approaching bus)
is a related but separate transform, deferred until the detector/TraCI
wiring it needs (P4.2, P6.1) is in place.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from xml.etree import ElementTree as ET


class TrafficLightNotFoundError(ValueError):
    """Raised when the requested `<tlLogic>` id does not exist in the network."""


class PhaseCountMismatchError(ValueError):
    """Raised when `phase_durations` doesn't match the tlLogic's current phase count."""


@dataclass(frozen=True)
class SignalRetimingResult:
    """Outcome of retiming one traffic light's phase durations."""

    net_xml: str
    previous_durations: list[float]
    previous_cycle_length_s: float
    new_cycle_length_s: float


def retime_signal(
    net_xml: str,
    *,
    tls_id: str,
    phase_durations: list[float],
) -> SignalRetimingResult:
    """Set the `duration` of each `<phase>` on `<tlLogic id=tls_id>` in `net_xml`.

    `net_xml` is not mutated: the result's `net_xml` is a new document.
    `phase_durations` is applied in order to the existing phases, and must
    have exactly as many entries as the tlLogic currently has phases.

    Raises `TrafficLightNotFoundError` if no `<tlLogic id=tls_id>` exists,
    `PhaseCountMismatchError` if the lengths differ, and `ValueError` if any
    duration is not positive.
    """
    if any(duration <= 0 for duration in phase_durations):
        raise ValueError("every phase duration must be positive")

    root = ET.fromstring(net_xml)
    tl_logic = _find_tl_logic(root, tls_id)
    if tl_logic is None:
        raise TrafficLightNotFoundError(f"no tlLogic with id {tls_id!r}")

    phases = tl_logic.findall("phase")
    if len(phases) != len(phase_durations):
        raise PhaseCountMismatchError(
            f"tlLogic {tls_id!r} has {len(phases)} phase(s), "
            f"got {len(phase_durations)} duration(s)"
        )
    previous_durations = [float(phase.get("duration", 0)) for phase in phases]

    new_root = deepcopy(root)
    new_tl_logic = _find_tl_logic(new_root, tls_id)
    assert new_tl_logic is not None  # same lookup as above, just confirmed to exist
    for phase, duration in zip(new_tl_logic.findall("phase"), phase_durations, strict=True):
        phase.set("duration", _format_duration(duration))

    return SignalRetimingResult(
        net_xml=ET.tostring(new_root, encoding="unicode"),
        previous_durations=previous_durations,
        previous_cycle_length_s=sum(previous_durations),
        new_cycle_length_s=sum(phase_durations),
    )


def _find_tl_logic(root: ET.Element, tls_id: str) -> ET.Element | None:
    for tl_logic in root.findall("tlLogic"):
        if tl_logic.get("id") == tls_id:
            return tl_logic
    return None


def _format_duration(duration: float) -> str:
    return str(int(duration)) if duration == int(duration) else str(duration)
