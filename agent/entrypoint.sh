#!/bin/bash
echo "[BUBBLE] Container started at $(date)"
ip addr show 2>&1 || echo "[BUBBLE] no ip command"
/usr/local/bin/syscall_logger.sh &
echo "[BUBBLE] Starting agent..."
exec python3 /home/prisoner/agent.py