import argparse

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def get_experiment_metadata(dir: str, tool: str) -> str:
    rps = ""
    metadata = ""
    scenario_name = dir.split('/')[-1]
    if tool == "wrk":
        # then the directory name would be of the form scenario-<n_threads>-<n_duration>-<n_connections>
        parts = scenario_name.split('-')
        n_threads = parts[1]
        n_duration = parts[2]
        n_connections = parts[3]

        metadata = f"Threads: {n_threads}, Connections: {n_connections}, Duration: {n_duration}"

    elif tool == "go-wrk":
        # then the directory name would be of the form scenario-<n_duration>-<n_connections>
        parts = scenario_name.split('-')
        n_duration = parts[1]
        n_connections = parts[2]

        metadata = f"Connections: {n_connections}, Duration: {n_duration}"

    elif tool == "k6":
        # then the directory name would be of the form scenario-<n_duration>-<n_vus>
        parts = scenario_name.split('-')
        n_duration = parts[1]
        n_vus = parts[2]

        metadata = f"VUs: {n_vus}, Duration: {n_duration}"

    elif tool == "wrk2":
        # then the directory name would be of the form scenario-<n_threads>-<n_duration>-<n_connections>-<n_rate>
        parts = scenario_name.split('-')
        n_threads = parts[1]
        n_duration = parts[2]
        n_connections = parts[3]
        n_rate = parts[4]

        metadata = f"Threads: {n_threads}, Connections: {n_connections}, Duration: {n_duration}, Rate: {n_rate}"
    
    # read the dir/rps file and return the value
    with open(f"{dir}/rps", 'r') as f:
        rps = f.read()
    
    return f"{metadata}, RPS: {rps}"


def plot_csv(dir: str, output: str, tool: str):

    df = pd.read_csv(f"{dir}/results.csv")
    # Set the color palette
    sns.set_palette("deep")
    colors = sns.color_palette("deep")

    fig, ax1 = plt.subplots()

    sns.lineplot(x='Time (s)', y='CPU (%)', data=df, ax=ax1, color=colors[0], markers=True)
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('CPU (%)', color=colors[0])
    ax1.tick_params(axis='y', labelcolor=colors[0])

    ax2 = ax1.twinx()
    sns.lineplot(x='Time (s)', y='MEM (kB)', data=df, ax=ax2, color=colors[1], markers=True)
    ax2.set_ylabel('MEM (kB)', color=colors[1])
    ax2.tick_params(axis='y', labelcolor=colors[1])

    metadata = get_experiment_metadata(dir, tool)

    plt.title(f'{tool} - {metadata}')

    fig.tight_layout()
    plt.savefig(output)
    plt.close()


def parse_args():
    parser = argparse.ArgumentParser(description='Plot the data from a CSV file')
    parser.add_argument('-d', '--dir', type=str, required=True, help='Path to the output directory')
    parser.add_argument('-o', '--output', type=str, required=True, help='Path to the output image')
    parser.add_argument('-t', '--tool', type=str, required=True, help='Benchmarking tool used to generate the data')
    return parser.parse_args()

# Example usage
if __name__ == '__main__':
    args = parse_args()
    plot_csv(args.dir, args.output, args.tool)

