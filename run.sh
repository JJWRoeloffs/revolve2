#!/usr/bin/env bash

for config in "$@"; do
    python3 -m adv_symmetry "$config" &
done

trap 'kill $(jobs -p)' EXIT

for job in $(jobs -p); do
    wait $job
done
