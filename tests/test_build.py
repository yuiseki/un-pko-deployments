import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import build as B  # noqa: E402


def fc():
    p = {"mission": "UNDOF", "date": "20250516", "label": "NEPAL", "inner": "", "stack": 1, "no_warranty": "ABSOLUTELY NO WARRANTY"}
    return {"mission": "UNDOF", "map_date": "20250516", "based_on": "Based on United Nations map", "source_sha256": "ab",
            "tool_commit": "cd", "disclaimer": "ABSOLUTELY NO WARRANTY",
            "features": [{"geometry": {"coordinates": [36.0, 33.0]}, "properties": {**p, "stack": 2}},
                         {"geometry": {"coordinates": [35.9, 33.1]}, "properties": p}]}


def test_points_are_one_per_row_in_a_fixed_order_with_the_disclaimer():
    r = B.rows(fc(), "UNDOF_20250516_ab.geojson")
    assert [x["stack"] for x in r] == [1, 2]
    assert r[0]["lon"] == 35.9 and r[0]["disclaimer"] == "ABSOLUTELY NO WARRANTY" and "date" not in r[0]


def test_a_reference_number_is_found_whole_only():
    assert B.leaked("map 2916 here", ["2916"]) == ["2916"]
    assert B.leaked("29160 and 12916", ["2916"]) == []
