#!/bin/bash
# External dependencies:
# - https://www.selenic.com/smem/
# - https://stedolan.github.io/jq/
# - iproute2 (for ss command)
set -eEuo pipefail

trap 'last_command=$BASH_COMMAND; signal_received="EXIT"; cleanup; exit 0' EXIT
trap 'last_command=$BASH_COMMAND; signal_received="INT"; trap - INT; cleanup; kill -INT $$' INT
trap 'last_command=$BASH_COMMAND; signal_received="TERM"; trap - TERM; cleanup; kill -TERM $$' TERM
trap 'last_command=$BASH_COMMAND; signal_received="ERR"; cleanup; exit 1' ERR

# Create temp files to store the output of each collection command.
cpuf=$(mktemp)
memf=$(mktemp)
bandwidthf=$(mktemp)
sockf=$(mktemp)
error_log=$(mktemp)

function cleanup {
  exit_status=$?
  echo "Received signal: $signal_received"
  echo "Last command: $last_command"
  echo "Exit status: $exit_status"


  # rm -f "$cpuf" "$memf" "$bandwidthf" "$sockf" "$error_log"
}

rm -f results.csv
touch results.csv

# Redirect all stdout to both the console and the error_log file
exec > >(tee -a "$error_log") 2>&1

echo "cpu file: $cpuf"
echo "mem file: $memf"
echo "bandwidth file: $bandwidthf"
echo "sock file: $sockf"
echo "error log: $error_log"

# 5s is the default interval between samples.
# Note that this might be greater if either smem or the k6 API takes more time
# than this to return a response.
sint="${BENCH_SAMPLE_INTERVAL:-5}"

url=${BENCHMARK_URL:-http://localhost:8080}
url_without_protocol=$(echo "$url" | sed 's|http[s]*://||; s|/$||')
echo "benchmarking $url endpoint ($url_without_protocol) with tool $TOOL"
echo "benchmark url: ${BENCHMARK_URL}<"
device=$(ip route get "$url_without_protocol" | awk '{for (i=1; i<NF; i++) if ($i == "dev") print $(i+1)}')

if [ -z "${TOOL:-}" ]; then
  echo "TOOL environment variable must be set to specify the tool to benchmark"
  exit 1
fi
tool=${TOOL}

exp_dir="${EXPERIMENT_DIR}"
results_file="${exp_dir}/results.csv"
out_file="${exp_dir}/out.txt"

echo "error log: $error_log"

# Maximum bandwidth capacity in KB/s (e.g., 1 Gbps = 125000 KB/s)
# Get the maximum bandwidth capacity using ethtool
max_bandwidth_mbps=$(sudo ethtool "$device" | awk '/Speed:/ {print $2}' | sed 's/Mb\/s//')
if [ -z "$max_bandwidth_mbps" ]; then
  echo "Error: Unable to determine max bandwidth for device $device"
  exit 1
fi
max_bandwidth_kbps=$((max_bandwidth_mbps * 1024 / 8))

echo "using device $device with max bandwidth $max_bandwidth_kbps KB/s"

# Run the collection processes in parallel to avoid blocking.
# For details see https://stackoverflow.com/a/68316571

all_subprocess_pids=()
if [ "$tool" == "locust" ]; then
  nohup "$tool" "$@" --host="$url" >$out_file 2>&1 &
  pid="$!"
  all_subprocess_pids=$(pgrep -f "$tool ")
elif [ "$tool" == "k6" ]; then
  "$tool" "$@" -e URL="$url" >$out_file 2>&1 &
  pid="$!"
else
  "$tool" "$@" $url >$out_file 2>&1 &
  pid="$!"
fi

echo "pid is $pid"
echo '"Time (s)","CPU (%)","MEM (KB)","Bandwidth (KB/s)","Bandwidth Utilization (%)","Open Sockets"' > $results_file
while true; do
  # Check if the process is still running
  if [ "$tool" == "locust" ]; then
    all_locust_pids=$(pgrep -f "$tool ")
    if [ -z "$all_locust_pids" ]; then
      echo "Error: Locust process has terminated. Exiting loop."
      cleanup
      exit 1
    fi
  elif ! ps -p "$pid" > /dev/null; then
    echo "Process $pid has terminated. Exiting loop."
    cleanup
    exit 0
  fi
  
  echo "Collecting metrics for process $pid"

  etimes=$(ps -p "$pid" --no-headers -o etimes | awk '{ print $1 }')
  if [ $? -ne 0 ]; then
    echo "Error: Failed to get elapsed time for process $pid"
    exit 1
  fi

  pids=()
  { exec >"$bandwidthf" 2>>"$error_log"; sudo ifstat -i "$device" "$sint" 1 | awk 'NR==3 {print $1 + $2}'; } &
  pids+=($!)

  if [ "$tool" == "locust" ]; then
    all_locust_pids=$(pgrep -f "$tool ")
    all_lpid_str=$(echo $all_locust_pids | xargs | sed 's/[^ ]\+/-p &/g')
    n_pids=$(echo $all_locust_pids | wc -w)
    echo "all locust pids: $all_locust_pids"

    {
      exec >"$cpuf" 2>>"$error_log";
      all_locust_pids=$(pgrep -f "locust")
      pid_array=($all_locust_pids)
      chunk_size=5
      total_sum=0
      # echo "new iteration" >> ./chunk.txt
      for((i=0; i< $n_pids; i+=chunk_size)); do
        chunk=${pid_array[@]:i:chunk_size}
        # echo $chunk >> ./chunk.txt
        chunk_sum=$(sudo top -b -n 2 -d "$sint" -p $(echo $chunk | tr ' ' ',') | awk '/PID USER/{last_line_found=1; next} last_line_found && /locust/ { sum += $9 } END { print sum }';)
        if [ -z "$chunk_sum" ]; then
          chunk_sum=0
        fi
        # echo "$total_sum + $chunk_sum" >> ./chunk.txt
        total_sum=$(echo "$total_sum + $chunk_sum" | bc)
      done
      if [ -z "$total_sum" ]; then
        total_sum=0
      fi
      echo $total_sum
    } &
    pids+=($!)

    {
      exec >"$memf" 2>>"$error_log";
      sudo smem -H -U "$USER" -c 'pid pss' -P "$tool" | {
        grep -E "$all_locust_pids" || echo 0; } | awk '{ sum += $NF } END { print sum }';
    } & 
    pids+=($!)

  else 
    { 
      exec >"$cpuf" 2>>"$error_log"; top -b -n 2 -d "$sint" -p "$pid" | {
        grep "$pid" || echo; } | tail -1 | awk '{print (NF>0 ? $9 : "0")}'; 
    } &
    pids+=($!)

    { exec >"$memf" 2>>"$error_log"; sudo smem -H -U "$USER" -c 'pid pss' -P "$tool" | {
        grep "$pid" || echo 0; } | awk '{ sum += $NF } END { print sum }'; } &
    pids+=($!)

  fi

  { exec >"$sockf" 2>>"$error_log"; sudo ss -tp | grep -c "$tool" || true; } &
  pids+=($!)

  trap - EXIT
  trap - INT
  trap - TERM
  trap - ERR
  wait "${pids[@]}" && echo "All background processes completed successfully"
  waitstatus=$?
  if [ $waitstatus -ne 0 ]; then
    echo "Error: One or more background processes failed with exit status $waitstatus"
    cat "$error_log"

    cleanup
    exit 1
  fi
  trap 'last_command=$BASH_COMMAND; signal_received="EXIT"; cleanup; exit 0' EXIT
  trap 'last_command=$BASH_COMMAND; signal_received="INT"; trap - INT; cleanup; kill -INT $$' INT
  trap 'last_command=$BASH_COMMAND; signal_received="TERM"; trap - TERM; cleanup; kill -TERM $$' TERM
  trap 'last_command=$BASH_COMMAND; signal_received="ERR"; cleanup; exit 1' ERR
  
  bandwidth=$(cat "$bandwidthf")
  bandwidth_utilization=$(awk -v bw="$bandwidth" -v max_bw="$max_bandwidth_kbps" 'BEGIN { printf "%.2f", (bw / max_bw) * 100 }')
  open_sockets=$(cat "$sockf")
  echo "${etimes},$(cat "$cpuf"),$(cat "$memf"),${bandwidth},${bandwidth_utilization},${open_sockets}" >> $results_file
done