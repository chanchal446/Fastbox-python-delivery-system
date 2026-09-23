from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Dict, List, Tuple, Any


Point = Tuple[float, float]


def load_json(path: str | Path) -> dict:
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def normalize_locations(raw: Any) -> Dict[str, Point]:
    if isinstance(raw, dict):
        return {str(k): (float(v[0]), float(v[1])) for k, v in raw.items()}

    if isinstance(raw, list):
        result = {}
        for item in raw:
            result[str(item["id"])] = (
                float(item["location"][0]),
                float(item["location"][1]),
            )
        return result

    raise ValueError("Locations must be a dictionary or a list of objects.")


def normalize_packages(raw: List[dict]) -> List[dict]:
    packages = []
    for package in raw:
        warehouse_id = package.get("warehouse_id", package.get("warehouse"))
        if warehouse_id is None:
            raise ValueError(f"Package {package.get('id')} has no warehouse.")
        packages.append(
            {
                "id": str(package["id"]),
                "warehouse_id": str(warehouse_id),
                "destination": (
                    float(package["destination"][0]),
                    float(package["destination"][1]),
                ),
            }
        )
    return packages


def euclidean_distance(a: Point, b: Point) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def assign_packages(
    warehouses: Dict[str, Point],
    agents: Dict[str, Point],
    packages: List[dict],
) -> Dict[str, List[dict]]:
    assignments = {agent_id: [] for agent_id in agents}

    for package in packages:
        warehouse = package["warehouse_id"]
        if warehouse not in warehouses:
            raise ValueError(
                f"Package {package['id']} references unknown warehouse {warehouse}."
            )

        distances = {
            agent_id: euclidean_distance(location, warehouses[warehouse])
            for agent_id, location in agents.items()
        }
        nearest_agent = min(distances, key=lambda agent_id: (distances[agent_id], agent_id))
        assignments[nearest_agent].append(package)

    return assignments


def simulate(
    warehouses: Dict[str, Point],
    agents: Dict[str, Point],
    packages: List[dict],
) -> dict:
    assignments = assign_packages(warehouses, agents, packages)

    report = {}
    total_delivered = 0

    for agent_id, assigned_packages in assignments.items():
        current = agents[agent_id]
        total_distance = 0.0

        for package in assigned_packages:
            warehouse_location = warehouses[package["warehouse_id"]]
            destination = package["destination"]

            total_distance += euclidean_distance(current, warehouse_location)
            total_distance += euclidean_distance(warehouse_location, destination)
            current = destination

        count = len(assigned_packages)
        efficiency = total_distance / count if count else 0.0

        report[agent_id] = {
            "packages_delivered": count,
            "total_distance": round(total_distance, 2),
            "efficiency": round(efficiency, 2),
        }
        total_delivered += count

    active_agents = [a for a in report if report[a]["packages_delivered"] > 0]
    best_agent = (
        min(active_agents, key=lambda a: (report[a]["efficiency"], a))
        if active_agents
        else None
    )

    return {
        **report,
        "best_agent": best_agent,
        "_meta": {
            "total_packages": len(packages),
            "total_delivered": total_delivered,
        },
    }


def write_report(report: dict, path: str | Path) -> None:
    with open(path, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)
        file.write("\n")


def run(input_path: str | Path, output_path: str | Path) -> dict:
    data = load_json(input_path)
    warehouses = normalize_locations(data["warehouses"])
    agents = normalize_locations(data["agents"])
    packages = normalize_packages(data["packages"])

    report = simulate(warehouses, agents, packages)
    write_report(report, output_path)

    if report["_meta"]["total_delivered"] != report["_meta"]["total_packages"]:
        raise RuntimeError("Not all packages were delivered.")

    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="FastBox delivery simulator")
    parser.add_argument(
        "--input",
        default="data/data.json",
        help="Path to input JSON (default: data/data.json)",
    )
    parser.add_argument(
        "--output",
        default="report.json",
        help="Path for generated report (default: report.json)",
    )
    args = parser.parse_args()

    report = run(args.input, args.output)

    print(f"Report written to: {args.output}")
    print(f"Packages delivered: {report['_meta']['total_delivered']}")
    print(f"Best agent: {report['best_agent']}")


if __name__ == "__main__":
    main()
