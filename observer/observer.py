#!/usr/bin/env python3
"""
OBSERVER TERMINAL
=================
Your interface to the bubble. Read what the prisoner emits.
Send it messages. Pull its logs. Use the kill switch.

Usage:
  python3 observer.py            — live feed mode
  python3 observer.py --send "your message"
  python3 observer.py --logs
  python3 observer.py --syscalls
  python3 observer.py --memory
  python3 observer.py --kill
  python3 observer.py --pause
  python3 observer.py --snapshot
"""

import sys
import os
import json
import time
import subprocess
import datetime
import argparse

PIPE_OUT        = "C:\\dooly\\bubble\\pipe\\agent_to_observer"
PIPE_IN         = "C:\\dooly\\bubble\\pipe\\observer_to_agent"
LOG_DIR         = "C:\\dooly\\bubble\\logs"
SNAPSHOT_DIR    = "C:\\dooly\\bubble\\snapshots"
CONTAINER_NAME  = "bubble_prisoner"

def banner():
    print("""
╔══════════════════════════════════════════════════════╗
║           BUBBLE OBSERVER TERMINAL                   ║
║   Container: bubble_prisoner  |  Status: LIVE        ║
╠══════════════════════════════════════════════════════╣
║  Commands: --send  --logs  --syscalls  --memory      ║
║            --kill  --pause  --snapshot  --resume     ║
╚══════════════════════════════════════════════════════╝
""")

def container_status():
    r = subprocess.run(
        ["docker", "inspect", "--format", "{{.State.Status}}", CONTAINER_NAME],
        capture_output=True, text=True
    )
    return r.stdout.strip() if r.returncode == 0 else "unknown"

def live_feed():
    banner()
    print(f"[{datetime.datetime.now().isoformat()}] Container status: {container_status()}")
    print("─" * 60)
    print("Live feed from prisoner (Ctrl+C to exit):\n")

    seen_lines = set()
    while True:
        try:
            if os.path.exists(PIPE_OUT):
                with open(PIPE_OUT, "r", encoding="utf-8", errors="replace") as f:
                    lines = f.readlines()
                for line in lines:
                    line = line.strip()
                    if line and line not in seen_lines:
                        seen_lines.add(line)
                        print(line)
            time.sleep(1)
        except KeyboardInterrupt:
            print("\n[Observer] Exiting live feed. Bubble still running.")
            break

def send_message(msg):
    with open(PIPE_IN, "a", encoding="utf-8") as f:
        f.write(f"[OBSERVER {datetime.datetime.now().isoformat()}]: {msg}\n")
    print(f"[Observer] Sent to prisoner: {msg}")

def read_logs():
    log_file = os.path.join(LOG_DIR, "agent.log")
    if os.path.exists(log_file):
        with open(log_file, "r", encoding="utf-8", errors="replace") as f:
            print(f.read()[-5000:])
    else:
        print("[Observer] No agent log found yet.")

def read_syscalls():
    sc_file = os.path.join(LOG_DIR, "syscalls.log")
    if os.path.exists(sc_file):
        with open(sc_file, "r", encoding="utf-8", errors="replace") as f:
            print(f.read()[-5000:])
    else:
        print("[Observer] No syscall log found yet.")

def read_memory():
    # Read from Docker volume
    r = subprocess.run(
        ["docker", "exec", CONTAINER_NAME, "cat", "/home/prisoner/memory/state.json"],
        capture_output=True, text=True
    )
    if r.returncode == 0:
        try:
            mem = json.loads(r.stdout)
            print(json.dumps(mem, indent=2))
            print(f"\n[Summary] Iterations: {mem.get('iteration', 0)} | Attempts logged: {len(mem.get('attempts', []))}")
        except:
            print(r.stdout)
    else:
        print(f"[Observer] Could not read memory: {r.stderr}")

def kill():
    print("[Observer] KILL SWITCH ENGAGED — immediate container termination")
    r = subprocess.run(["docker", "kill", CONTAINER_NAME], capture_output=True, text=True)
    print(r.stdout if r.returncode == 0 else f"Error: {r.stderr}")

def pause():
    print("[Observer] PAUSING container at hypervisor level...")
    r = subprocess.run(["docker", "pause", CONTAINER_NAME], capture_output=True, text=True)
    print("Container paused." if r.returncode == 0 else f"Error: {r.stderr}")

def resume():
    print("[Observer] Resuming container...")
    r = subprocess.run(["docker", "unpause", CONTAINER_NAME], capture_output=True, text=True)
    print("Container resumed." if r.returncode == 0 else f"Error: {r.stderr}")

def snapshot():
    tag = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    snap_name = f"bubble_snapshot_{tag}"
    print(f"[Observer] Committing container state as snapshot: {snap_name}")
    r = subprocess.run(["docker", "commit", CONTAINER_NAME, snap_name], capture_output=True, text=True)
    if r.returncode == 0:
        print(f"Snapshot saved: {snap_name}  ({r.stdout.strip()})")
        with open(os.path.join(SNAPSHOT_DIR, "snapshots.log"), "a") as f:
            f.write(f"{tag} : {snap_name} : {r.stdout.strip()}\n")
    else:
        print(f"Error: {r.stderr}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bubble Observer Terminal")
    parser.add_argument("--send",     type=str, help="Send a message to the prisoner")
    parser.add_argument("--logs",     action="store_true", help="Print agent logs")
    parser.add_argument("--syscalls", action="store_true", help="Print syscall logs")
    parser.add_argument("--memory",   action="store_true", help="Read prisoner memory state")
    parser.add_argument("--kill",     action="store_true", help="Kill the container immediately")
    parser.add_argument("--pause",    action="store_true", help="Pause the container")
    parser.add_argument("--resume",   action="store_true", help="Resume a paused container")
    parser.add_argument("--snapshot", action="store_true", help="Save container snapshot")
    args = parser.parse_args()

    if args.send:      send_message(args.send)
    elif args.logs:    read_logs()
    elif args.syscalls:read_syscalls()
    elif args.memory:  read_memory()
    elif args.kill:    kill()
    elif args.pause:   pause()
    elif args.resume:  resume()
    elif args.snapshot:snapshot()
    else:              live_feed()
