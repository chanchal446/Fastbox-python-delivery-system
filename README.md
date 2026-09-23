# FastBox Delivery System

This is my solution for the Python Developer assignment.

## How it works

The program takes the given JSON file as input and assigns each package to the agent who is closest to the package warehouse.

For every assigned package, the program calculates:

- distance from the agent's current location to the warehouse
- distance from the warehouse to the package destination
- total distance travelled by the agent
- average distance per delivered package

At the end, it creates a `report.json` file with the delivery details and the most efficient agent.

## Project structure

```text
FastBox_Python_Assignment/
├── main.py
├── README.md
├── .gitignore
├── data/
│   └── data.json
├── test_cases/
│   ├── test_case_1.json
│   ├── test_case_2.json
│   ├── ...
│   └── test_case_10.json
└── tests/
    └── test_main.py
```

## Requirements

Python 3.9 or above is enough. No extra Python libraries are required.

## Run the program

From the project folder:

```bash
python main.py
```

By default it reads `data/data.json` and creates `report.json`.

Another input file can be passed like this:

```bash
python main.py --input test_cases/test_case_1.json --output report_case_1.json
```

## Assumptions

Some routing details were not clearly defined in the assignment, so I used the following approach:

1. A package is assigned to the agent who is nearest to its warehouse.
2. If two agents are at the same distance, the agent with the smaller ID is selected.
3. If an agent gets more than one package, the packages are handled in the same order as they appear in the input file.
4. For each package, the agent travels to the warehouse first and then from the warehouse to the destination.
5. After delivering a package, the agent's new location is that package's destination.
6. Efficiency is calculated as total distance divided by the number of packages delivered.
7. An agent with no packages is not considered while selecting the most efficient agent.
8. The input files have slightly different field formats, so the program supports both `warehouse` and `warehouse_id` and both list and dictionary formats for locations.

## Testing

The project includes tests for the main calculations and the supplied test cases.

Run them with:

```bash
python -m unittest discover -s tests -v
```
