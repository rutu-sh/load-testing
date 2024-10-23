import os
import argparse
from typing import List

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


TOOLS = ["wrk", "go-wrk", "k6", "wrk2"]


# for every tool, and for every scenario, calculate the average CPU Load and Memory Usage 
# Put everything together in a single dataframe against the RPS value
# Plot Average CPU Load and Memory Usage against RPS for every tool


def get_rps(dir: str) -> float:
    with open(f"{dir}/rps", 'r') as f:
        return float(f.read())
    

def get_tool_scenarios(results_dir: str, tool: str) -> List[str]:
    print("results_dir", results_dir)
    return [f for f in os.listdir(results_dir) if os.path.isdir(f"{results_dir}/{f}") and f.startswith("scenario-")]


def get_all_scenario_data(results_dir: str) -> pd.DataFrame:
    processed_stats = pd.DataFrame(
        columns=["Tool", "Scenario", "RPS", "CPU (%)", "MEM (kB)"]
    )
    for tool in TOOLS:
        scenarios = get_tool_scenarios(f"{results_dir}/{tool}/results", tool)
        scenarios_dirs = list(map(lambda x: f"{results_dir}/{tool}/results/{x}", scenarios))

        for scenario, scenario_dir in zip(scenarios, scenarios_dirs):
            print(f"Processing {tool} {scenario_dir}")
            rps = get_rps(scenario_dir)
            stats = pd.read_csv(f"{scenario_dir}/results.csv")
            stats["RPS"] = rps
            stats["Scenario"] = scenario
            stats["Tool"] = tool
            processed_stats = pd.concat([processed_stats, stats])

    return processed_stats


def parse_args():
    parser = argparse.ArgumentParser(description="Plot results")
    parser.add_argument(
        "--results-dir",
        type=str,
        required=True,
        help="Path to the directory containing the results",
    )
    parser.add_argument(
        "-o"
        "--output",
        type=str,
        required=True,
        help="Path to the output directory",
    )

    return parser.parse_args()


def main():
    args = parse_args()
    df = get_all_scenario_data(args.results_dir)
    df.to_csv("all_results.csv", index=False)


if __name__ == "__main__":
    main()