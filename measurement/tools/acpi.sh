#!/bin/bash

if [ $# -eq 0 ]; then
    echo "Usage: $0 <total_duration_in_seconds>"
    exit 1
fi

total_duration=$1
start_time=$(date +%s)

while true
do
    current_time=$(date +%s)
    elapsed_time=$((current_time - start_time))

    if [ "$elapsed_time" -ge "$total_duration" ]; then
        echo "Monitoring completed. Total duration: $total_duration seconds."
        break
    fi

    power=$(sensors | grep -i 'power1' | tail -n 1)
    echo "$power"
    sleep 1
done
