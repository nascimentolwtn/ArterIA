"""Population per TAZ (roadmap P3.2, ADR 0017): the production side of the
gravity-model fallback. Reads IBGE Censo 2022 population-by-census-tract
("setor censitário") data straight out of IBGE's GeoPackage (a SQLite file,
read with the stdlib `sqlite3` — no GDAL/fiona dependency) and sums each
setor's population into whichever TAZ contains its centroid.

The one real network call (`download_setores_gpkg`) is isolated behind an
injected `download` callable, per ADR 0009 — same seam as
`osm_fetch.py`'s `download_source_pbf`. Everything else (GeoPackage geometry
decoding, the zone join) is pure and exercised here against toy fixtures.

The attraction side (jobs/land-use proxy, per ADR 0017) is not implemented
yet: no Geosanja zoning layer has been downloaded for SJC (see
`.claude/napkin.md`), so this module only covers production weights.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Callable
from pathlib import Path

import shapely
from pydantic import BaseModel
from shapely.geometry import Point, shape

from arteria.demand.zoning import EXTERNAL_ZONE_ID, ZonePolygon, load_zones_from_study_areas

IBGE_SETORES_GPKG_URL_TEMPLATE = (
    "https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/"
    "Agregados_por_Setores_Censitarios/malha_com_atributos/setores/gpkg/UF/"
    "{uf}/{uf}_setores_CD2022.gpkg"
)
_GPKG_ENVELOPE_BYTES = {0: 0, 1: 32, 2: 48, 3: 48, 4: 64}


class Setor(BaseModel):
    id: str
    population: int
    lon: float
    lat: float


class PopulationSummary(BaseModel):
    population_by_zone: dict[str, int]
    total_population: int
    setor_count: int


def _urlretrieve(url: str, dest: Path) -> None:
    """Real default for `download_setores_gpkg`'s `download` parameter. Not
    exercised remotely (ADR 0009: no network access) — tests always inject
    a fake `download` instead."""
    import urllib.request

    urllib.request.urlretrieve(url, dest)  # noqa: S310 - desk-only, real fetch


def download_setores_gpkg(
    uf: str, dest: Path, *, download: Callable[[str, Path], None] = _urlretrieve
) -> Path:
    """Downloads IBGE's state-level setor GeoPackage (geometry + Censo 2022
    attributes already joined) to `dest`. ~180 MB for São Paulo state; not
    committed (gitignored under `/data/`, like other raw IBGE downloads)."""
    url = IBGE_SETORES_GPKG_URL_TEMPLATE.format(uf=uf)
    dest.parent.mkdir(parents=True, exist_ok=True)
    download(url, dest)
    return dest


def _gpkg_geometry_to_point(blob: bytes) -> Point:
    """Decodes a GeoPackage geometry blob (GP header + envelope + standard
    WKB) and returns its centroid. GPKG header: bytes 0-1 'GP', byte 2
    version, byte 3 flags (bits 1-3 select the envelope size)."""
    flags = blob[3]
    envelope_indicator = (flags >> 1) & 0x07
    offset = 8 + _GPKG_ENVELOPE_BYTES[envelope_indicator]
    geometry = shapely.from_wkb(blob[offset:])
    return geometry.centroid


def load_setores(
    gpkg_path: str | Path,
    table: str,
    municipality_code: str,
    connect: Callable[[str], sqlite3.Connection] = sqlite3.connect,
) -> list[Setor]:
    """Reads every setor for `municipality_code` (IBGE's 7-digit `CD_MUN`)
    out of `table` in the GeoPackage at `gpkg_path`, with its Censo 2022
    total population (`V0001`) and centroid (lon, lat)."""
    con = connect(str(gpkg_path))
    try:
        cur = con.execute(
            f'SELECT CD_SETOR, V0001, geom FROM "{table}" WHERE CD_MUN = ?',  # noqa: S608
            (municipality_code,),
        )
        setores = []
        for setor_id, population, geom_blob in cur.fetchall():
            centroid = _gpkg_geometry_to_point(geom_blob)
            setores.append(
                Setor(id=setor_id, population=population, lon=centroid.x, lat=centroid.y)
            )
        return setores
    finally:
        con.close()


def population_by_zone(setores: list[Setor], zones: list[ZonePolygon]) -> dict[str, int]:
    """Sums each setor's population into whichever zone polygon contains its
    centroid, or `EXTERNAL_ZONE_ID` otherwise. WGS84 throughout (setor
    centroids and the study-area polygons are both lon/lat already, so no
    net-offset/UTM transform is needed here, unlike `zoning.py`'s edges)."""
    zone_polygons = [(zone.id, shape(zone.geometry)) for zone in zones]
    totals: dict[str, int] = {zone.id: 0 for zone in zones}
    totals[EXTERNAL_ZONE_ID] = 0

    for setor in setores:
        point = Point(setor.lon, setor.lat)
        zone_id = next((zid for zid, poly in zone_polygons if poly.contains(point)), None)
        totals[zone_id if zone_id is not None else EXTERNAL_ZONE_ID] += setor.population

    return totals


def build_population_summary(
    city_dir: str | Path, municipality_code: str, table: str, gpkg_path: str | Path
) -> PopulationSummary:
    """Orchestrator: loads `<city_dir>/study-areas.geojson`'s zones and the
    GeoPackage's setores for `municipality_code`, and sums population by
    zone."""
    zones = load_zones_from_study_areas(Path(city_dir) / "study-areas.geojson")
    setores = load_setores(gpkg_path, table, municipality_code)
    totals = population_by_zone(setores, zones)
    return PopulationSummary(
        population_by_zone=totals,
        total_population=sum(totals.values()),
        setor_count=len(setores),
    )
