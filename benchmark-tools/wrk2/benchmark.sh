#!/bin/bash
# External dependencies:
# - https://www.selenic.com/smem/
# - https://stedolan.github.io/jq/
set -eEuo pipefail

trap 'cleanup; exit 0' EXIT
trap 'trap - INT; cleanup; kill -INT $$' INT
trap 'trap - TERM; cleanup; kill -TERM $$' TERM

# Create temp files to store the output of each collection command.
cpuf=$(mktemp)
memf=$(mktemp)

cleanup() {
  rm -f "$cpuf" "$memf" 
}

rm -f results.csv
touch results.csv

# 5s is the default interval between samples.
# Note that this might be greater if either smem or the k6 API takes more time
# than this to return a response.
sint="${BENCH_SAMPLE_INTERVAL:-5}"

wrk2 "$@" >out.txt 2>&1 &
pid="$!"

# Run the collection processes in parallel to avoid blocking.
# For details see https://stackoverflow.com/a/68316571

echo '"Time (s)","CPU (%)","MEM (kB)"' >> results.csv
while true; do
  etimes=$(ps -p "$pid" --no-headers -o etimes | awk '{ print $1 }')
  pids=()
  { exec >"$cpuf"; top -b -n 2 -d "$sint" -p "$pid" | {
      grep "$pid" || echo; } | tail -1 | awk '{print (NF>0 ? $9 : "0")}'; } &
  pids+=($!)
  { exec >"$memf"; smem -H -U "$USER" -c 'pid pss' -P 'wrk2 ' | {
      grep "$pid" || echo 0; } | awk '{ print $NF }'; } &
  pids+=($!)
  wait "${pids[@]}"
  echo "${etimes},$(cat "$cpuf"),$(cat "$memf")" >> results.csv
done