#!/bin/bash
# Run 64 parallel freerouting jobs with shuffled DSN files using xvfb-run
JAVA=${FREEROUTE_JAVA:-/usr/lib/jvm/java-21-openjdk-amd64/bin/java}
JAR=~/freeroute_runs/freerouting-1.9.0-executable.jar
DIR=~/freeroute_runs

echo "Starting 64 parallel freerouting jobs at $(date)"
echo "Using Java: $JAVA"

for i in $(seq 0 63); do
    ii=$(printf "%03d" $i)
    dsn=$DIR/run_${ii}.dsn
    ses=$DIR/run_${ii}.ses
    log=$DIR/run_${ii}.log
    if [ -f "$dsn" ]; then
        xvfb-run -a $JAVA -Xmx2g -jar $JAR -de "$dsn" -do "$ses" -mp 100 > "$log" 2>&1 &
    fi
done

echo "All 64 jobs launched ($(jobs -p | wc -l) PIDs), waiting..."
wait

echo "All jobs complete at $(date)"
echo ""
echo "=== RESULTS ==="
best_run=""
best_count=999
for i in $(seq 0 63); do
    ii=$(printf "%03d" $i)
    log=$DIR/run_${ii}.log
    result=$(grep "pass #" "$log" 2>/dev/null | tail -1 | grep -oP "\d+ unrouted" || echo "no result")
    count=$(echo "$result" | grep -oP "^\d+" || echo 999)
    echo "run_${ii}: $result"
    if [ "$count" -lt "$best_count" ] 2>/dev/null; then
        best_count=$count
        best_run=$ii
    fi
done
echo ""
echo "BEST: run_${best_run} with ${best_count} unrouted"
