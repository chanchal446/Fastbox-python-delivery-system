import json
import tempfile
import unittest
from pathlib import Path

from main import (
    euclidean_distance,
    normalize_locations,
    normalize_packages,
    assign_packages,
    run,
)


ROOT = Path(__file__).resolve().parents[1]


class FastBoxTests(unittest.TestCase):
    def test_euclidean_distance(self):
        self.assertAlmostEqual(euclidean_distance((0, 0), (3, 4)), 5.0)

    def test_assignment(self):
        warehouses = {"W1": (0, 0), "W2": (50, 75)}
        agents = {"A1": (5, 5), "A2": (60, 60)}
        packages = normalize_packages([
            {"id": "P1", "warehouse": "W1", "destination": [10, 10]},
            {"id": "P2", "warehouse": "W2", "destination": [70, 90]},
        ])
        result = assign_packages(warehouses, agents, packages)
        self.assertEqual([p["id"] for p in result["A1"]], ["P1"])
        self.assertEqual([p["id"] for p in result["A2"]], ["P2"])

    def test_base_case_delivers_every_package(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "report.json"
            report = run(ROOT / "data" / "data.json", output)

            self.assertEqual(report["_meta"]["total_packages"], 5)
            self.assertEqual(report["_meta"]["total_delivered"], 5)
            self.assertTrue(output.exists())

            saved = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(saved["_meta"]["total_delivered"], 5)

    def test_all_supplied_cases(self):
        test_dir = ROOT / "test_cases"
        files = sorted(test_dir.glob("test_case_*.json"))
        self.assertEqual(len(files), 10)

        for input_file in files:
            with self.subTest(input=input_file.name):
                with tempfile.TemporaryDirectory() as tmp:
                    output = Path(tmp) / "report.json"
                    report = run(input_file, output)
                    self.assertEqual(
                        report["_meta"]["total_packages"],
                        report["_meta"]["total_delivered"],
                    )


if __name__ == "__main__":
    unittest.main()
