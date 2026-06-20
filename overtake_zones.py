"""
Overtake Mode Zone Reference Table (2026+ F1 seasons)
---------------------------------------------------------
NOTE ON 2026 REGULATION CHANGE:
DRS was removed from the F1 regulations starting in 2026. It has been
replaced by two separate systems:

  1. "Straight Mode" (Active Aero) — automatic drag-reduction sections
     that EVERY car uses on every lap, regardless of proximity to another
     car. This is closer in spirit to "fast sections of track" than an
     overtaking aid.

  2. "Overtake Mode" (formerly "Manual Override Mode") — the actual
     overtaking aid that replaces old DRS. Activates extra MGU-K power
     for a trailing car within 1 second of the car ahead, at designated
     zones. THIS is the 2026-era equivalent of "DRS zones" for modeling
     overtaking difficulty.

This module tracks Overtake Mode zone counts, since that's the feature
conceptually equivalent to the old DRS zone count (proximity-gated,
overtake-specific). If you'd rather model raw straight-line speed
opportunity instead, track Straight Mode zones — that's a different
feature with different meaning, not a 1:1 swap for this one.

DATA RELIABILITY WARNING:
As of mid-2026, official zone counts/lengths are not consistently
published per-circuit. Only entries with a verified source are filled
in below. Everything else is marked TODO with circuit_data_verified=False.
DO NOT treat TODO rows as zero zones — that's "unknown," not "none."
Update this table as the FIA publishes more official track maps over
the season (check formula1.com circuit guides and FIA race documents).

Usage:
    from overtake_zones import get_overtake_zone_info, OVERTAKE_ZONES_2026

    info = get_overtake_zone_info("albert_park")
    print(info)
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class OvertakeZoneInfo:
    circuit_id: str
    circuit_name: str
    zone_count: Optional[int]          # number of Overtake Mode activation zones; None if unknown
    longest_zone_m: Optional[int]      # length of the longest zone in meters; None if unknown
    verified: bool                     # True if sourced from an official/confirmed reference
    source_note: str                   # where this came from, or why it's still a TODO


# ---------------------------------------------------------------------------
# 2026 Overtake Mode zone table
# ---------------------------------------------------------------------------
# Fill in `zone_count` / `longest_zone_m` and flip `verified=True` as you
# confirm each circuit from FIA race documents or official F1 circuit guides.
# Circuit IDs loosely match common FastF1 / Ergast naming conventions —
# adjust to match whatever your other modules use as keys.

OVERTAKE_ZONES_2026: dict[str, OvertakeZoneInfo] = {
    "albert_park": OvertakeZoneInfo(
        circuit_id="albert_park",
        circuit_name="Albert Park Circuit (Australian GP)",
        zone_count=None,
        longest_zone_m=None,
        verified=False,
        source_note=(
            "5 Straight Mode (Active Aero) sections confirmed for 2026 "
            "(Sector 1 straight T2-T3, T5-T6 loop, Sector 2 descent after T8, "
            "T10-T11 section, pit straight). Overtake Mode zone count specifically "
            "is NOT yet confirmed separately from Straight Mode — sources conflict "
            "on whether Overtake Mode has 1 detection point or multiple. "
            "TODO: confirm from official FIA Australian GP race documents."
        ),
    ),
    "bahrain": OvertakeZoneInfo(
        circuit_id="bahrain",
        circuit_name="Bahrain International Circuit",
        zone_count=None,
        longest_zone_m=None,
        verified=False,
        source_note=(
            "Pre-season testing host; track maps referenced but exact Overtake "
            "Mode zone count/length not confirmed in sources checked. Some "
            "reporting suggests an activation zone near Turn 1. "
            "TODO: confirm from official FIA Bahrain GP race documents."
        ),
    ),
    "shanghai": OvertakeZoneInfo(
        circuit_id="shanghai",
        circuit_name="Shanghai International Circuit",
        zone_count=None,
        longest_zone_m=None,
        verified=False,
        source_note="Track map not yet published as of early 2026 per sources checked. TODO.",
    ),
    "suzuka": OvertakeZoneInfo(
        circuit_id="suzuka",
        circuit_name="Suzuka International Racing Course",
        zone_count=None,
        longest_zone_m=None,
        verified=False,
        source_note="Track map not yet published as of early 2026 per sources checked. TODO.",
    ),
    # --- Add remaining 2026 calendar circuits below as you confirm them ---
    # "miami": OvertakeZoneInfo("miami", "Miami International Autodrome", None, None, False, "TODO"),
    # "imola": OvertakeZoneInfo("imola", "Autodromo Enzo e Dino Ferrari", None, None, False, "TODO"),
    # "monaco": OvertakeZoneInfo("monaco", "Circuit de Monaco", None, None, False, "TODO"),
    # "barcelona": OvertakeZoneInfo("barcelona", "Circuit de Barcelona-Catalunya", None, None, False, "TODO"),
    # "montreal": OvertakeZoneInfo("montreal", "Circuit Gilles Villeneuve", None, None, False, "TODO"),
    # "spielberg": OvertakeZoneInfo("spielberg", "Red Bull Ring", None, None, False, "TODO"),
    # "silverstone": OvertakeZoneInfo("silverstone", "Silverstone Circuit", None, None, False, "TODO"),
    # "spa": OvertakeZoneInfo("spa", "Circuit de Spa-Francorchamps", None, None, False, "TODO"),
    # "hungaroring": OvertakeZoneInfo("hungaroring", "Hungaroring", None, None, False, "TODO"),
    # "zandvoort": OvertakeZoneInfo("zandvoort", "Circuit Zandvoort", None, None, False, "TODO"),
    # "monza": OvertakeZoneInfo("monza", "Autodromo Nazionale Monza", None, None, False, "TODO"),
    # "baku": OvertakeZoneInfo("baku", "Baku City Circuit", None, None, False, "TODO"),
    # "marina_bay": OvertakeZoneInfo("marina_bay", "Marina Bay Street Circuit", None, None, False, "TODO"),
    # "cota": OvertakeZoneInfo("cota", "Circuit of the Americas", None, None, False, "TODO"),
    # "mexico_city": OvertakeZoneInfo("mexico_city", "Autodromo Hermanos Rodriguez", None, None, False, "TODO"),
    # "interlagos": OvertakeZoneInfo("interlagos", "Autodromo Jose Carlos Pace", None, None, False, "TODO"),
    # "las_vegas": OvertakeZoneInfo("las_vegas", "Las Vegas Strip Circuit", None, None, False, "TODO"),
    # "lusail": OvertakeZoneInfo("lusail", "Lusail International Circuit", None, None, False, "TODO"),
    # "yas_marina": OvertakeZoneInfo("yas_marina", "Yas Marina Circuit", None, None, False, "TODO"),
}


def get_overtake_zone_info(circuit_id: str) -> OvertakeZoneInfo:
    """
    Look up Overtake Mode zone info for a circuit.

    Raises KeyError with a clear message if the circuit isn't in the table
    at all (vs. returning a misleading default).
    """
    if circuit_id not in OVERTAKE_ZONES_2026:
        raise KeyError(
            f"'{circuit_id}' not found in OVERTAKE_ZONES_2026. "
            f"Known circuit IDs: {sorted(OVERTAKE_ZONES_2026.keys())}"
        )
    return OVERTAKE_ZONES_2026[circuit_id]


def get_overtake_zone_count(circuit_id: str, default_if_unverified: Optional[int] = None) -> Optional[int]:
    """
    Convenience accessor for just the zone count, for feeding into a model.

    Args:
        circuit_id: Circuit lookup key.
        default_if_unverified: Value to return if this circuit's data isn't
            verified yet (e.g. you might pass the historical DRS zone count
            from 2025 as a rough placeholder — but this WILL be wrong in
            magnitude since Overtake Mode zones don't map 1:1 to old DRS
            zones, so use with caution and prefer leaving as None/NaN
            in your training data until verified).

    Returns:
        zone_count if verified, else default_if_unverified (None unless specified).
    """
    info = get_overtake_zone_info(circuit_id)
    if info.verified and info.zone_count is not None:
        return info.zone_count
    return default_if_unverified


def unverified_circuits() -> list[str]:
    """Return circuit_ids still needing verification — useful as a maintenance checklist."""
    return [cid for cid, info in OVERTAKE_ZONES_2026.items() if not info.verified]


if __name__ == "__main__":
    print(f"Circuits in table: {len(OVERTAKE_ZONES_2026)}")
    print(f"Verified: {len(OVERTAKE_ZONES_2026) - len(unverified_circuits())}")
    print(f"Still TODO: {len(unverified_circuits())}")
    print()
    for cid in unverified_circuits():
        info = OVERTAKE_ZONES_2026[cid]
        print(f"TODO [{cid}]: {info.circuit_name}")
        print(f"   {info.source_note}")
        print()
