import os
import re
import json

import pandas as pd


def calculate_averages(exp_results_path: str) -> dict:
    """
        Calculate the following stats from the results.csv file: 
            1. AVG(CPU (%))
            2. AVG(Memory (KB))
            3. AVG(Bandwidth (KB/s))
            4. AVG(Bandwidth Utilization (%))
            5. AVG(Open Sockets)
    """
    df = pd.read_csv(exp_results_path)
    df.fillna(0, inplace=True)
    return {
        "avg_cpu": df['CPU (%)'].mean(),
        "avg_memory": df['MEM (KB)'].mean(),
        "avg_bandwidth": df['Bandwidth (KB/s)'].mean(),
        "avg_bandwidth_utilization": df['Bandwidth Utilization (%)'].mean(),
        "avg_open_sockets": df['Open Sockets'].mean()
    }


def duration_to_seconds(duration: str) -> int:
    """
    Convert duration to seconds
    """
    if 'm' in duration:
        return int(duration[:-1]) * 60
    elif 'h' in duration:
        return int(duration[:-1]) * 3600
    elif 's' in duration:
        return int(duration[:-1])
    else:
        return None
    
def get_wrk_rps(out_path: str) -> int:
    """
    Get the requests per second from the wrk output file
    """
    with open(out_path, 'r') as f:
        for line in f:
            if 'Requests/sec' in line:
                return float(line.split()[1])
    return None

def get_ab_rps(out_path: str) -> int:
    """
    Get the requests per second from the ab output file
    """
    with open(out_path, 'r') as f:
        for line in f:
            if 'Requests per second' in line:
                return float(line.split()[3])
    return None

def get_locust_rps(out_path: str) -> int:
    """
    Get the requests per second from the locust output file
    """
    with open(out_path, 'r') as f:
        for line in f:
            if 'Aggregated' in line:
                return float(line.split()[9])
    return None

def process_wrk_data(exp_dir: str) -> pd.DataFrame:
    """
        Extract the following from the exp_metadata.json:
            1. Number of threads (-t or --threads)
            2. Number of connections (-c or --connections)
            3. Duration of the test (-d or --duration)
    """
    RE_THREAD_PATTERN = re.compile(r'-t|--threads')
    RE_CONNECTION_PATTERN = re.compile(r'-c|--connections')
    RE_DURATION_PATTERN = re.compile(r'-d|--duration')

    experiments = os.listdir(exp_dir)
    data = []
    for exp in experiments:
        exp_metadata_path = os.path.join(exp_dir, exp, 'exp_metadata.json')
        with open(exp_metadata_path, 'r') as f:
            exp_metadata = json.load(f)

        try:
            parameters = exp_metadata['parameters']
            new_data = {
                "tool": "wrk",
                "exp_name": exp,
                "threads": None,
                "connections": None,
                "duration": None,
                "results_path": os.path.join(exp_dir, exp, 'results.csv'),
                "out_path": os.path.join(exp_dir, exp, 'out.txt'),
                "rps": get_wrk_rps(os.path.join(exp_dir, exp, 'out.txt'))
            }
            for param in parameters:
                if re.match(RE_THREAD_PATTERN, param):
                    new_data["threads"] = param.split()[-1] if param.split()[-1].isdigit() else None
                elif re.match(RE_CONNECTION_PATTERN, param):
                    new_data["connections"] = param.split()[-1] if param.split()[-1].isdigit() else None
                elif re.match(RE_DURATION_PATTERN, param):
                    new_data["duration"] = duration_to_seconds(param.split()[-1])
                else:
                    continue
                
            avg_stats = calculate_averages(new_data["results_path"])
            new_data.update(avg_stats) 
            data.append(new_data)

        except KeyError:
            print(f"Could not find parameters in {exp_metadata_path}")
            continue

    return pd.DataFrame(data)


def process_wrk2_data(exp_dir: str) -> pd.DataFrame:
    """
    Extract the following from the exp_metadata.json:
        1. Number of threads (-t or --threads)
        2. Number of connections (-c or --connections)
        3. Duration of the test (-d or --duration)
        4. Rate limiting (-R or --rate)
    """
    RE_THREAD_PATTERN = re.compile(r'-t|--threads')
    RE_CONNECTION_PATTERN = re.compile(r'-c|--connections')
    RE_DURATION_PATTERN = re.compile(r'-d|--duration')
    RE_RATE_PATTERN = re.compile(r'-R|--rate')

    experiments = os.listdir(exp_dir)
    data = []
    for exp in experiments:
        exp_metadata_path = os.path.join(exp_dir, exp, 'exp_metadata.json')
        with open(exp_metadata_path, 'r') as f:
            exp_metadata = json.load(f)

        try:
            parameters = exp_metadata['parameters']
            new_data = {
                "tool": "wrk2",
                "exp_name": exp,
                "threads": None,
                "connections": None,
                "duration": None,
                "rate": None,
                "results_path": os.path.join(exp_dir, exp, 'results.csv'),
                "out_path": os.path.join(exp_dir, exp, 'out.txt'),
                "rps": get_wrk_rps(os.path.join(exp_dir, exp, 'out.txt'))
            }
            for param in parameters:
                if re.match(RE_THREAD_PATTERN, param):
                    new_data["threads"] = param.split()[-1] if param.split()[-1].isdigit() else None
                elif re.match(RE_CONNECTION_PATTERN, param):
                    new_data["connections"] = param.split()[-1] if param.split()[-1].isdigit() else None
                elif re.match(RE_DURATION_PATTERN, param):
                    new_data["duration"] = duration_to_seconds(param.split()[-1])
                elif re.match(RE_RATE_PATTERN, param):
                    new_data["rate"] = param.split()[-1]
                else:
                    continue
            
            avg_stats = calculate_averages(new_data["results_path"])
            new_data.update(avg_stats) 
            data.append(new_data)

        except KeyError:
            print(f"Could not find parameters in {exp_metadata_path}")
            continue

    return pd.DataFrame(data)


def process_oha_data(exp_dir: str) -> pd.DataFrame:
    """
    Extract the following from the metadata.json:
        1. Duration of the test (-z)
        2. Number of connections (-c)
        3. Query per second (-q)
        4. Disable Keepalive (--disable-keepalive) or not
    """
    RE_DURATION_PATTERN = re.compile(r'-z')
    RE_CONNECTION_PATTERN = re.compile(r'-c')
    RE_QPS_PATTERN = re.compile(r'-q')
    RE_KEEPALIVE_PATTERN = re.compile(r'--disable-keepalive')

    experiments = os.listdir(exp_dir)
    data = []
    for exp in experiments:
        exp_metadata_path = os.path.join(exp_dir, exp, 'exp_metadata.json')
        with open(exp_metadata_path, 'r') as f:
            exp_metadata = json.load(f)

        try:
            parameters = exp_metadata['parameters']
            new_data = {
                "tool": "oha",
                "exp_name": exp,
                "duration": None,
                "connections": None,
                "qps": None,
                "disable_keepalive": False,
                "results_path": os.path.join(exp_dir, exp, 'results.csv'),
                "out_path": os.path.join(exp_dir, exp, 'out.txt'),
                "rps": get_wrk_rps(os.path.join(exp_dir, exp, 'out.txt'))
            }
            for param in parameters:
                if re.match(RE_DURATION_PATTERN, param):
                    new_data["duration"] = duration_to_seconds(param.split()[-1])
                elif re.match(RE_CONNECTION_PATTERN, param):
                    new_data["connections"] = param.split()[-1] if param.split()[-1].isdigit() else None
                elif re.match(RE_QPS_PATTERN, param):
                    new_data["qps"] = param.split()[-1] if param.split()[-1].isdigit() else None
                elif re.match(RE_KEEPALIVE_PATTERN, param):
                    new_data["disable_keepalive"] = True
                else:
                    continue
            
            avg_stats = calculate_averages(new_data["results_path"])
            new_data.update(avg_stats) 
            data.append(new_data)

        except KeyError:
            print(f"Could not find parameters in {exp_metadata_path}")
            continue

    return pd.DataFrame(data)


def process_ab_data(exp_dir: str) -> pd.DataFrame:
    """
    Extract the following from the metadata.json:
        1. Number of connections (-c)
        2. Number of threads (-t)
        3. Disable Keepalive (-k)
        4. Number of requests (-n)
    """
    RE_CONNECTION_PATTERN = re.compile(r'-c')
    RE_THREAD_PATTERN = re.compile(r'-t')
    RE_KEEPALIVE_PATTERN = re.compile(r'-k')
    RE_REQUESTS_PATTERN = re.compile(r'-n')

    experiments = os.listdir(exp_dir)
    data = []
    for exp in experiments:
        exp_metadata_path = os.path.join(exp_dir, exp, 'exp_metadata.json')
        with open(exp_metadata_path, 'r') as f:
            exp_metadata = json.load(f)

        try:
            parameters = exp_metadata['parameters']
            new_data = {
                "tool": "ab",
                "exp_name": exp,
                "connections": None,
                "threads": None,
                "disable_keepalive": True,
                "requests": None,
                "results_path": os.path.join(exp_dir, exp, 'results.csv'),
                "out_path": os.path.join(exp_dir, exp, 'out.txt'),
                "rps": get_ab_rps(os.path.join(exp_dir, exp, 'out.txt'))
            }
            for param in parameters:
                if re.match(RE_CONNECTION_PATTERN, param):
                    new_data["connections"] = param.split()[-1] if param.split()[-1].isdigit() else None
                elif re.match(RE_THREAD_PATTERN, param):
                    new_data["threads"] = param.split()[-1] if param.split()[-1].isdigit() else None
                elif re.match(RE_KEEPALIVE_PATTERN, param):
                    new_data["disable_keepalive"] = False
                elif re.match(RE_REQUESTS_PATTERN, param):
                    new_data["n_requests"] = param.split()[-1] if param.split()[-1].isdigit() else None
                else:
                    continue
                
            avg_stats = calculate_averages(new_data["results_path"])
            new_data.update(avg_stats) 
            data.append(new_data)

        except KeyError:
            print(f"Could not find parameters in {exp_metadata_path}")
            continue

    return pd.DataFrame(data)

def process_locust_data(exp_dir: str) -> pd.DataFrame:
    """
    Extract the following from the metadata.json:
        1. Number of users (-u or --users)
        2. Config file (-f or --locustfile)
        3. Spawn rate (-r or --spawn-rate)
        4. Number of worker processes (--processes)
        5. Run time (-t or --run-time)
    """
    RE_USERS_PATTERN = re.compile(r'-u|--users')
    RE_CONFIG_PATTERN = re.compile(r'-f|--locustfile')
    RE_SPAWN_RATE_PATTERN = re.compile(r'-r|--spawn-rate')
    RE_PROCESSES_PATTERN = re.compile(r'--processes')
    RE_RUN_TIME_PATTERN = re.compile(r'-t|--run-time')

    experiments = os.listdir(exp_dir)
    data = []
    for exp in experiments:
        exp_metadata_path = os.path.join(exp_dir, exp, 'exp_metadata.json')
        with open(exp_metadata_path, 'r') as f:
            exp_metadata = json.load(f)

        try:
            parameters = exp_metadata['parameters']
            new_data = {
                "tool": "locust",
                "exp_name": exp,
                "users": None,
                "config_file": None,
                "spawn_rate": None,
                "processes": None,
                "run_time": None,
                "results_path": os.path.join(exp_dir, exp, 'results.csv'),
                "out_path": os.path.join(exp_dir, exp, 'out.txt'),
                "rps": get_locust_rps(os.path.join(exp_dir, exp, 'out.txt'))
            }
            for param in parameters:
                if re.match(RE_USERS_PATTERN, param):
                    new_data["users"] = param.split()[-1] if param.split()[-1].isdigit() else None
                elif re.match(RE_CONFIG_PATTERN, param):
                    new_data["config_file"] = param.split()[-1]
                elif re.match(RE_SPAWN_RATE_PATTERN, param):
                    new_data["spawn_rate"] = param.split()[-1] if param.split()[-1].isdigit() else None
                elif re.match(RE_PROCESSES_PATTERN, param):
                    new_data["processes"] = param.split()[-1] if param.split()[-1].isdigit() else None
                elif re.match(RE_RUN_TIME_PATTERN, param):
                    new_data["run_time"] = duration_to_seconds(param.split()[-1])
                else:
                    continue
                
            avg_stats = calculate_averages(new_data["results_path"])
            new_data.update(avg_stats) 
            data.append(new_data)

        except KeyError:
            print(f"Could not find parameters in {exp_metadata_path}")
            continue

    return pd.DataFrame(data)




def main():
    os.makedirs('results', exist_ok=True)

    exp_dir = 'experiments/wrk'
    wrk_data = process_wrk_data(exp_dir)
    wrk_data.to_csv('results/wrk.csv', index=False)
    print(wrk_data)

    exp_dir = 'experiments/wrk2'
    wrk2_data = process_wrk2_data(exp_dir)
    wrk2_data.to_csv('results/wrk2.csv', index=False)
    print(wrk2_data)

    exp_dir = 'experiments/oha'
    oha_data = process_oha_data(exp_dir)
    oha_data.to_csv('results/oha.csv', index=False)
    print(oha_data)

    exp_dir = 'experiments/ab'
    ab_data = process_ab_data(exp_dir)
    ab_data.to_csv('results/ab.csv', index=False)
    print(ab_data)

    exp_dir = 'experiments/locust'
    locust_data = process_locust_data(exp_dir)
    locust_data.to_csv('results/locust.csv', index=False)
    print(locust_data)



if __name__ == '__main__':
    main()