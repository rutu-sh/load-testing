import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from typing import List


class ResultsMetrics:
    TIME = "Time (s)"
    CPU  = "CPU (%)"
    MEM  = "MEM (KB)"
    BANDWIDTH = "Bandwidth (KB/s)"
    BANDWIDTH_UTIL = "Bandwidth Utilization (%)"
    OPEN_SOCKETS = "Open Sockets"

class Experiment:
    name: str
    tool: str

    def __init__(self, name: str, tool: str):
        self.name = name
        self.tool = tool


snake_cased_strings = {
    "Time (s)": "time",
    "CPU (%)": "cpu",
    "MEM (KB)": "mem",
    "Bandwidth (KB/s)": "bandwidth",
    "Bandwidth Utilization (%)": "bandwidth_util",
    "Open Sockets": "open_sockets"
}




def get_tool_data(tool: str, results_dir: str) -> pd.DataFrame:
    # Read the data
    wrk_data = pd.read_csv(f"{results_dir}/{tool}.csv")
    return wrk_data


def plot_rps_vs_avg_cpu(df: pd.DataFrame, tool: str):
    # Plot the data
    fig = px.scatter(df, x="avg_cpu", y="rps", color="exp_name", title="RPS vs Avg CPU", color_discrete_sequence=px.colors.qualitative.Dark24)
    fig.update_layout(legend=dict(x=1.05, y=1))
    fig.write_image(f"plots/{tool}_rps_vs_avg_cpu.png")


def plot_rps_vs_avg_mem(df: pd.DataFrame, tool: str):
    # Plot the data
    fig = px.scatter(
        df, 
        x="avg_memory", 
        y="rps", 
        color="exp_name", 
        title="RPS vs Avg Mem",
        color_discrete_sequence=px.colors.qualitative.Dark24)
    fig.update_layout(legend=dict(x=1.05, y=1))
    fig.write_image(f"plots/{tool}_rps_vs_avg_mem.png")


def compare_two_experiments(tool: str, exp1: str, exp2: str, metric_y: str, metric_x: str = ResultsMetrics.TIME):
    # Get the data 
    df_exp1 = pd.read_csv(f"experiments/{tool}/{exp1}/results.csv")
    df_exp2 = pd.read_csv(f"experiments/{tool}/{exp2}/results.csv")

    # merge the data
    df_exp1["exp_name"] = exp1
    df_exp2["exp_name"] = exp2
    df = pd.concat([df_exp1, df_exp2])

    # Plot the data
    fig = px.line(df, x=metric_x, y=metric_y, color="exp_name", title=f"{metric_y} vs {metric_x}")
    fig.update_layout(legend=dict(x=1.05, y=1))
    fig.write_image(f"plots/{tool}_{exp1}_vs_{exp2}_{snake_cased_strings[metric_y]}_vs_{snake_cased_strings[metric_x]}.png")


def compare_experiments(tool: str, exps: list, metric_y: str, metric_x: str = ResultsMetrics.TIME):
    # Get the data 
    df = pd.DataFrame()

    for exp in exps:
        df_exp = pd.read_csv(f"experiments/{tool}/{exp}/results.csv")
        df_exp["exp_name"] = exp
        df = pd.concat([df, df_exp])

    # Plot the data
    fig = px.line(df, x=metric_x, y=metric_y, color="exp_name", title=f"{metric_y} vs {metric_x}")
    fig.update_layout(legend=dict(x=1.05, y=1))
    fig.write_image(f"plots/{tool}_{'_'.join(exps)}_{snake_cased_strings[metric_y]}_vs_{snake_cased_strings[metric_x]}.png")


def compare_experiments_grid(exps: List[Experiment]):
    # create the subplots
    metrics_y = [ResultsMetrics.CPU, ResultsMetrics.MEM, ResultsMetrics.BANDWIDTH_UTIL, ResultsMetrics.OPEN_SOCKETS]
    metrics_x = [ResultsMetrics.TIME for _ in metrics_y]

    # colors = px.colors.qualitative.Dark24
    colors = px.colors.qualitative.Plotly
    exp_colors = {exp.name: colors[i] for i, exp in enumerate(exps)}

    # read the data
    df = pd.DataFrame()
    for exp in exps:
        df_exp = pd.read_csv(f"experiments/{exp.tool}/{exp.name}/results.csv")
        df_exp["exp_name"] = exp.name
        df = pd.concat([df, df_exp])

    fig = make_subplots(rows=2, cols=2, subplot_titles=[
        f"{metric_y} vs {metric_x}" for metric_y, metric_x in zip(metrics_y, metrics_x)
    ])

    for i, (metric_y, metric_x) in enumerate(zip(metrics_y, metrics_x)):
        for exp in exps:
            df_exp = df[df["exp_name"] == exp.name]
            trace = go.Scatter(x=df_exp[metric_x], y=df_exp[metric_y], mode="lines", name=exp.name, line=dict(color=exp_colors[exp.name]), showlegend=(i == 0))
            fig.add_trace(trace, row=(i // 2) + 1, col=(i % 2) + 1)
    
    fig.update_layout(
        legend=dict(x=1.05, y=1)
    )
    fig.write_image(f"plots/{'_'.join([exp.name for exp in exps])}_comparison.png")

def main():
    # Get the data
    # wrk_data = get_tool_data("wrk", "results")

    # Plot the data
    # plot_rps_vs_avg_cpu(wrk_data, "wrk")
    # plot_rps_vs_avg_mem(wrk_data, "wrk")
    # compare_two_experiments("wrk", "wrk-1", "wrk-2", ResultsMetrics.CPU, ResultsMetrics.TIME)
    # compare_two_experiments("wrk", "wrk-1", "wrk-2", ResultsMetrics.MEM, ResultsMetrics.TIME)
    # compare_two_experiments("wrk", "wrk-1", "wrk-2", ResultsMetrics.BANDWIDTH_UTIL, ResultsMetrics.TIME)
    # compare_two_experiments("wrk", "wrk-1", "wrk-2", ResultsMetrics.OPEN_SOCKETS, ResultsMetrics.TIME)
    # compare_experiments("wrk", ["wrk-3", "wrk-4", "wrk-5"], ResultsMetrics.CPU, ResultsMetrics.TIME)
    # compare_experiments("wrk", ["wrk-3", "wrk-4", "wrk-5"], ResultsMetrics.MEM, ResultsMetrics.TIME)
    # compare_experiments("wrk", ["wrk-3", "wrk-4", "wrk-5"], ResultsMetrics.BANDWIDTH_UTIL, ResultsMetrics.TIME)
    # compare_experiments("wrk", ["wrk-3", "wrk-4", "wrk-5"], ResultsMetrics.OPEN_SOCKETS, ResultsMetrics.TIME)

    # compare_experiments_grid([
    #     Experiment(name="wrk-1", tool="wrk"),
    #     Experiment(name="wrk-2", tool="wrk")
    # ])
    # compare_experiments_grid([
    #     Experiment(name="wrk-3", tool="wrk"),
    #     Experiment(name="wrk-4", tool="wrk"),
    #     Experiment(name="wrk-5", tool="wrk")
    # ])
    # compare_experiments_grid([
    #     Experiment(name="wrk-5", tool="wrk"),
    #     Experiment(name="wrk-6", tool="wrk"),
    #     Experiment(name="wrk-7", tool="wrk"),
    #     Experiment(name="wrk-8", tool="wrk")       
    # ])
    # compare_experiments_grid([
    #     Experiment(name="wrk-10", tool="wrk")
    # ])

    # wrk2_data = get_tool_data("wrk2", "results")
    # plot_rps_vs_avg_cpu(wrk2_data, "wrk2")
    # plot_rps_vs_avg_mem(wrk2_data, "wrk2")
    # compare_experiments_grid([
    #     Experiment(name="wrk2-1", tool="wrk2"),
    #     Experiment(name="wrk2-2", tool="wrk2"),
    #     Experiment(name="wrk2-3", tool="wrk2"),
    #     Experiment(name="wrk2-4", tool="wrk2")
    # ])
    # compare_experiments_grid([
    #     Experiment(name="wrk2-5", tool="wrk2"),
    #     Experiment(name="wrk2-6", tool="wrk2"),
    #     Experiment(name="wrk2-7", tool="wrk2"),
    #     Experiment(name="wrk2-8", tool="wrk2")
    # ])
    # compare_experiments_grid([
    #     Experiment(name="wrk2-8", tool="wrk2"),
    #     Experiment(name="wrk2-9", tool="wrk2"),
    # ])
    # compare_experiments_grid([
    #     Experiment(name="wrk2-8", tool="wrk2"),
    #     Experiment(name="wrk2-11", tool="wrk2")
    # ])
    # compare_experiments_grid([
    #     Experiment(name="wrk2-12", tool="wrk2"),
    #     Experiment(name="wrk2-13", tool="wrk2")
    # ])
    # compare_experiments_grid([
    #     Experiment(name="wrk2-13", tool="wrk2"),
    #     Experiment(name="wrk2-14", tool="wrk2")
    # ])
    # compare_experiments_grid([
    #     Experiment(name="oha-1", tool="oha"),
    #     Experiment(name="oha-2", tool="oha"),
    #     Experiment(name="oha-3", tool="oha"),
    #     Experiment(name="oha-4", tool="oha"),
    # ])
    # oha_data = get_tool_data("oha", "results")
    # plot_rps_vs_avg_cpu(oha_data, "oha")
    # plot_rps_vs_avg_mem(oha_data, "oha")

    #])
    # compare_experiments_grid([
    #     Experiment(name="locust-5", tool="locust"),
    #     Experiment(name="locust-6", tool="locust"),
    #     Experiment(name="locust-7", tool="locust")
    # ])
    # compare_experiments_grid([
    #     Experiment(name="locust-1", tool="locust"),
    #     Experiment(name="locust-5", tool="locust"),
    #     Experiment(name="locust-8", tool="locust"),
    #     Experiment(name="locust-11", tool="locust"),
    #     Experiment(name="locust-14", tool="locust"),
    #     Experiment(name="locust-17", tool="locust"),
    #     Experiment(name="locust-21", tool="locust"),
    # ])

    # compare_experiments_grid([
    #     Experiment(name="k6-1", tool="k6"),
    #     Experiment(name="k6-2", tool="k6")
    # ])

    # k6_data = get_tool_data("k6", "results")
    # plot_rps_vs_avg_cpu(k6_data, "k6")
    # plot_rps_vs_avg_mem(k6_data, "k6")

    # compare_experiments_grid([
    #     Experiment(name="k6-1", tool="k6"),
    #     Experiment(name="k6-2", tool="k6")
    # ])

    # ab_data = get_tool_data("ab", "results")
    # plot_rps_vs_avg_cpu(ab_data, "ab")
    # plot_rps_vs_avg_mem(ab_data, "ab")

    # compare_experiments_grid([
    #     Experiment(name="ab-1", tool="ab"),
    #     Experiment(name="ab-2", tool="ab"),
    #     Experiment(name="ab-3", tool="ab"),
    # ])

    # compare_experiments_grid([
    #     Experiment(name="k6-3", tool="k6"),
    #     Experiment(name="k6-4", tool="k6"),
    #     Experiment(name="k6-5", tool="k6"),
    #     Experiment(name="k6-6", tool="k6")
    # ])

    # compare_experiments_grid([
    #     Experiment(name="k6-7", tool="k6"),
    #     Experiment(name="k6-8", tool="k6"),
    #     Experiment(name="k6-9", tool="k6"),
    #     Experiment(name="k6-10", tool="k6")
    # ])

    # compare_experiments_grid([
    #     Experiment(name="k6-11", tool="k6"),
    #     Experiment(name="k6-12", tool="k6"),
    #     Experiment(name="k6-13", tool="k6"),
    #     Experiment(name="k6-14", tool="k6")
    # ])

    # compare_experiments_grid([
    #     Experiment(name="k6-6", tool="k6"),
    #     Experiment(name="k6-15", tool="k6"),
    # ])

    compare_experiments_grid([
        Experiment(name="oha-2", tool="oha"),
        Experiment(name="ab-2", tool="ab"),
        Experiment(name="locust-25", tool="locust"),
        Experiment(name="wrk-5", tool="wrk"),
        Experiment(name="wrk2-19", tool="wrk2"),
        Experiment(name="k6-9", tool="k6"),
    ])



if __name__ == "__main__":
    main()

