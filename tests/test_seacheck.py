import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import seacheck as S  # noqa: E402


def land_at(*lands):
    """A reverse geocoder with land only at the given (lat, lon) cells of 0.05 degrees."""
    cells = {(round(a / 0.05), round(o / 0.05)) for a, o in lands}

    def reverse(lat, lon):
        return (round(lat / 0.05), round(lon / 0.05)) in cells
    return reverse


def test_a_point_on_land_is_not_sea():
    assert not S.is_sea(5.0, -4.0, land_at((5.0, -4.0)))


def test_a_point_in_open_water_is_sea():
    assert S.is_sea(3.7, -3.9, land_at((5.4, -4.0)))


def test_a_point_a_little_off_the_coast_is_not_sea():
    # a unit on a coastal town's dot may fall a few hundred metres into the water: land within a cell of it
    assert not S.is_sea(5.0, -4.0, land_at((5.0, -3.95)))


def test_the_filter_drops_sea_points_and_counts_them(tmp_path):
    fc = {"type": "FeatureCollection", "mission": "UNOCI", "map_date": "20060905",
          "features": [{"type": "Feature", "geometry": {"type": "Point", "coordinates": [-4.0, 5.0]}, "properties": {}},
                       {"type": "Feature", "geometry": {"type": "Point", "coordinates": [-3.9, 3.7]}, "properties": {}}]}
    out, dropped = S.filter_sea(fc, land_at((5.0, -4.0)))
    assert len(out["features"]) == 1 and dropped == 1
    assert out["features"][0]["geometry"]["coordinates"] == [-4.0, 5.0]
