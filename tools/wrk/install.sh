function install() {
    sudo apt-get update -y && sudo apt-get install -y wrk
}


function benchmark() {
    # A function to benchmark wrk's performance
    # Usage: benchmark <url> <duration> <threads> <connections>
    # Writes results every second to a file
    url=$1
    duration=$2
    threads=$3
    connections=$4
    log_file=$5


    # run wrk in the background
    wrk -t $threads -c $connections -d $duration $url > wrk.log &

    # Get the PID of the wrk process
    pid=$!

    # Write the results to a file every second

    echo '"Time (s)","CPU (%)","RAM (kB)"'
    while true; do
    etimes=$(ps -p "$pid" --no-headers -o etimes | awk '{ print $1 }')
    pids=()
    { exec >"$cpuf"; top -b -n 2 -d "$sint" -p "$pid" | {
        grep "$pid" || echo; } | tail -1 | awk '{print (NF>0 ? $9 : "0")}'; } &
    pids+=($!)
    { exec >"$memf"; smem -H -U "$USER" -c 'pid pss' -P 'k6 run' | {
        grep "$pid" || echo 0; } | awk '{ print $NF }'; } &
    # pids+=($!)
    # { exec >"$vusf"; { curl -fsSL http://localhost:6565/v1/metrics/vus 2>/dev/null || echo '{}'
    #     } | jq '.data.attributes.sample.value // 0'; } &
    # pids+=($!)
    # { exec >"$rpsf"; { curl -fsSL http://localhost:6565/v1/metrics/http_reqs 2>/dev/null || echo '{}'
    #     } | jq '.data.attributes.sample.rate // 0'; } &
    # pids+=($!)
    wait "${pids[@]}"
    echo "${etimes},$(cat "$cpuf"),$(cat "$memf")"
    done

}