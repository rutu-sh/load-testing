#!/bin/bash
# External dependencies:
# - https://www.selenic.com/smem/
# - https://stedolan.github.io/jq/
# - iproute2 (for ss command)
set -eEuo pipefail

# trap 'last_command=$BASH_COMMAND; signal_received="EXIT"; cleanup; exit 0' EXIT
trap 'last_command=$BASH_COMMAND; signal_received="INT"; trap - INT; cleanup; kill -INT $$' INT
trap 'last_command=$BASH_COMMAND; signal_received="TERM"; trap - TERM; cleanup; kill -TERM $$' TERM

# Create temp files to store the output of each collection command.
cpuf=$(mktemp)
memf=$(mktemp)
bandwidthf=$(mktemp)
sockf=$(mktemp)
error_log=$(mktemp)

cleanup() {
  exit_status=$?
  echo "Received signal: $signal_received"
  echo "Last command: $last_command"
  echo "Exit status: $exit_status"
  rm -f "$cpuf" "$memf" "$bandwidthf" "$sockf" "$error_log"
}

rm -f results.csv
touch results.csv

# 5s is the default interval between samples.
# Note that this might be greater if either smem or the k6 API takes more time
# than this to return a response.
sint="${BENCH_SAMPLE_INTERVAL:-5}"

url=${BENCHMARK_URL:-http://localhost:8080}
url_without_protocol=$(echo "$url" | sed 's/http[s]*:\/\///')
echo "benchmarking $url with tool $TOOL"
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

"$tool" "$@" ${BENCHMARK_URL} >$out_file 2>&1 &
pid="$!"

echo "pid is $pid"
echo '"Time (s)","CPU (%)","MEM (KB)","Bandwidth (KB/s)","Bandwidth Utilization (%)","Open Sockets"' > $results_file
while true; do
  # Check if the process is still running
  if ! ps -p "$pid" > /dev/null; then
    echo "Process $pid has terminated. Exiting loop."
    cleanup
    exit 0
  fi
  
  echo "Collecting metrics for process $pid"

  etimes=$(ps -p "$pid" --no-headers -o etimes | awk '{ print $1 }')
  pids=()
  { exec >"$bandwidthf" 2>>"$error_log"; sudo ifstat -i "$device" "$sint" 1 | awk 'NR==3 {print $1 + $2}'; } &
  pids+=($!)
  { exec >"$cpuf" 2>>"$error_log"; top -b -n 2 -d "$sint" -p "$pid" | {
      grep "$pid" || echo; } | tail -1 | awk '{print (NF>0 ? $9 : "0")}'; } &
  pids+=($!)
  { exec >"$memf" 2>>"$error_log"; sudo smem -H -U "$USER" -c 'pid pss' -P "$tool" | {
      grep "$pid" || echo 0; } | awk '{ sum += $NF } END { print sum }'; } &
  pids+=($!)
  { exec >"$sockf" 2>>"$error_log"; sudo ss -tp | grep -c "$tool"; } &
  pids+=($!)

  trap - EXIT
  wait "${pids[@]}" 
  waitstatus=$?
  trap 'last_command=$BASH_COMMAND; signal_received="EXIT"; cleanup; exit 0' EXIT
  
  if [ $waitstatus -eq 0 ]; then
    echo "Metrics collected for process $pid at time $etimes"
  else
    echo "Error collecting metrics for process $pid at time $etimes"
    cat "$error_log"
    exit 1
  fi
  bandwidth=$(cat "$bandwidthf")
  bandwidth_utilization=$(awk -v bw="$bandwidth" -v max_bw="$max_bandwidth_kbps" 'BEGIN { printf "%.2f", (bw / max_bw) * 100 }')
  open_sockets=$(cat "$sockf")
  echo "${etimes},$(cat "$cpuf"),$(cat "$memf"),${bandwidth},${bandwidth_utilization},${open_sockets}" >> $results_file
done