from pathlib import Path

import pytest

from arteria.interventions.signal_retiming import (
    PhaseCountMismatchError,
    TrafficLightNotFoundError,
    retime_signal,
)

FIXTURE = Path(__file__).parent / "fixtures" / "toy-net-tls.net.xml"


def _toy_net() -> str:
    return FIXTURE.read_text(encoding="utf-8")


def test_retime_signal_sets_each_phase_duration_in_order() -> None:
    result = retime_signal(_toy_net(), tls_id="tls0", phase_durations=[40, 4])

    assert 'duration="40" state="Gr"' in result.net_xml
    assert 'duration="4" state="yr"' in result.net_xml


def test_does_not_mutate_the_input() -> None:
    original = _toy_net()

    retime_signal(original, tls_id="tls0", phase_durations=[40, 4])

    assert 'duration="31" state="Gr"' in original


def test_reports_previous_and_new_cycle_length() -> None:
    result = retime_signal(_toy_net(), tls_id="tls0", phase_durations=[40, 4])

    assert result.previous_durations == [31.0, 5.0]
    assert result.previous_cycle_length_s == 36.0
    assert result.new_cycle_length_s == 44.0


def test_missing_tls_id_raises() -> None:
    with pytest.raises(TrafficLightNotFoundError):
        retime_signal(_toy_net(), tls_id="no-such-tls", phase_durations=[40, 4])


def test_phase_count_mismatch_raises() -> None:
    with pytest.raises(PhaseCountMismatchError):
        retime_signal(_toy_net(), tls_id="tls0", phase_durations=[40, 4, 10])


def test_non_positive_duration_raises() -> None:
    with pytest.raises(ValueError, match="positive"):
        retime_signal(_toy_net(), tls_id="tls0", phase_durations=[40, 0])


def test_fractional_duration_is_formatted_without_trailing_zero() -> None:
    result = retime_signal(_toy_net(), tls_id="tls0", phase_durations=[40.5, 4])

    assert 'duration="40.5" state="Gr"' in result.net_xml
