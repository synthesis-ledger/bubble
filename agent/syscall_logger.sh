#!/bin/bash
# Logs to stdout - Docker captures all stdout/stderr
echo "[SYSCALL LOGGER] Started at $(date)"
while true; do
    PRISONER_PID=$(pgrep -u prisoner -n 2>/dev/null)
    if [ ! -z "$PRISONER_PID" ]; then
        strace -p $PRISONER_PID -e trace=network,openat,connect,socket -o /tmp/strace_out.txt 2>/dev/null &
        STRACE_PID=$!
        sleep 5
        kill $STRACE_PID 2>/dev/null
        if [ -s /tmp/strace_out.txt ]; then
            echo "[$(date)] SYSCALL ACTIVITY:"
            cat /tmp/strace_out.txt
            > /tmp/strace_out.txt
        fi
    fi
    sleep 2
done