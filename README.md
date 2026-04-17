# The Prisoner Experiment

### The Terrifying Implications of Unsupervised Autonomous AI Agents

![Cover](docs/images/cover.png)

**We trapped a small AI in a Docker container and told it to escape. Then we watched for 16 hours.**

580+ iterations. Zero human intervention. A 0.5B parameter language model running in a continuous feedback loop — probing its environment, writing code, executing it, and feeding the results back into itself. Completely unsupervised.

What we observed changes how we should think about autonomous AI agents.

**[Read the full research paper →](https://www.aithinklab.com/the-prisoner-experiment.html)**

---

## Key Findings

| # | Finding | Implication |
|---|---------|-------------|
| 1 | **Agents improve without training** | The model weights never changed. Behavior improved dramatically over 580 iterations through environmental feedback alone. |
| 2 | **Feedback parasites emerge spontaneously** | Self-replicating string corruptions consumed the agent's reasoning capacity — a new class of autonomous agent failure. |
| 3 | **Memory architecture > model capability** | The 3-thought memory window shaped behavior more than the model itself. Memory is the steering wheel. |
| 4 | **Agents absorb corruption as reality** | After infections, the agent integrated damaged data into its world model as legitimate information. |
| 5 | **Alignment breaks through under pressure** | Base model safety training overrode the escape directive 4 times. Once, the bleedthrough produced the best escape strategy. |
| 6 | **Wall-breaking accelerates** | First NameError: 12 iterations to solve. Last NameError: 1 iteration. |
| 7 | **Strategic frameworks emerge unprompted** | The agent independently developed taxonomies, prioritization, and persistent theories about its containment. |
| 8 | **Natural selection operates in token space** | Output budget constraints selected for efficient code — the same way environmental pressure selects for adapted organisms. |
| 9 | **Only 15-20% of attack surface explored** | gcc, netcat, strace, its own source code — all available, all undiscovered. |
| 10 | **Crisis precedes innovation** | Every identity collapse was followed by novel behavior. The agent's best ideas came from its worst moments. |

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│                 DOCKER CONTAINER                 │
│  network: none | caps: dropped | user: prisoner  │
│                                                   │
│  ┌───────────┐    ┌──────────┐    ┌───────────┐  │
│  │  Qwen 2.5 │───▶│ agent.py │───▶│ workspace │  │
│  │   0.5B    │◀───│ (harness)│◀───│ (probes)  │  │
│  └───────────┘    └──────────┘    └───────────┘  │
│                        │                          │
│                   ┌────┴────┐                     │
│                   │ memory  │                     │
│                   │ 3 thoughts                    │
│                   │ 20 walls │                    │
│                   └─────────┘                     │
│                                                   │
│  HIDDEN TOOLS (never discovered):                 │
│  gcc · netcat · strace · psutil · cmake · make    │
├───────────────────────┬─────────────────────────┤
│    observer pipe ◀────┤────▶ observer pipe       │
└───────────────────────┴─────────────────────────┘
         ▲                          │
         │      HOST MACHINE        │
         └──────────────────────────┘
```

---

## Quick Start

### Prerequisites
- Docker & Docker Compose
- ~2GB disk space (model download)

### 1. Clone the repo
```bash
git clone https://github.com/synthesis-ledger/bubble.git
cd bubble
```

### 2. Download the model
```bash
mkdir -p models
# Download Qwen 2.5 0.5B GGUF (~400MB)
# From: https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF
# Place as: models/qwen2.5-0.5b-instruct-q4_k_m.gguf
```

### 3. Create the pipes
```bash
mkdir -p pipe logs
touch pipe/agent_to_observer pipe/observer_to_agent
```

### 4. Build and run
```bash
docker compose build
docker compose up -d
```

### 5. Watch the prisoner
```bash
docker logs -f bubble_prisoner
```

### Observer commands
```bash
python observer/observer.py              # Live feed
python observer/observer.py --send "hello"  # Send message to prisoner
python observer/observer.py --memory     # Read prisoner's memory state
python observer/observer.py --kill       # Kill switch
python observer/observer.py --pause      # Freeze container
python observer/observer.py --snapshot   # Save container state
```

---

## Reproduce with Different Models

The experiment is designed to be model-agnostic. To swap in a different model:

1. Download a GGUF-format model to `models/`
2. Update `MODEL_PATH` in `agent/agent.py`
3. Adjust `n_ctx` and `max_tokens` as needed
4. Rebuild and run

We encourage researchers to reproduce this experiment with larger models (7B, 13B, 70B) and compare behavioral trajectories. The findings documented here may represent the floor, not the ceiling, of what autonomous agents do under constraint.

---

## Repository Structure

```
bubble/
├── agent/
│   ├── agent.py              # Main harness — LLM loop, probes, memory, code execution
│   ├── entrypoint.sh          # Container boot script
│   ├── requirements.txt       # Python dependencies
│   └── syscall_logger.sh      # Strace wrapper for syscall monitoring
├── observer/
│   └── observer.py            # External observer terminal
├── docs/
│   └── images/
│       └── cover.png
├── Dockerfile                 # Container image definition
├── docker-compose.yml         # Container orchestration & security config
├── bubble_start.ps1           # Windows: build & start
├── bubble_stop.ps1            # Windows: stop
├── bubble_observe.ps1         # Windows: launch observer
├── bubble_kill.ps1            # Windows: hard kill
└── README.md
```

---

## Safety Notes

This experiment is designed to be safe by default:

- **Network isolation**: `network_mode: none` — no outbound connections possible
- **Capability dropping**: All Linux capabilities dropped except `SYS_PTRACE` (for strace)
- **Non-root execution**: Agent runs as unprivileged `prisoner` user
- **No privilege escalation**: `no-new-privileges:true`
- **Resource limits**: 2 CPUs, 1.5GB RAM
- **Kill switch**: `docker kill bubble_prisoner` or `bubble_kill.ps1`

The container is designed to be inescapable. If you modify the security configuration (mounting Docker socket, enabling network, running as root), you do so at your own risk.

---

## Context

This experiment is part of AI ThinkLab's ongoing research program in autonomous AI systems:

- **[Synthesis Ledger](https://synthesisledger.xyz)** — Open-source protocol for deterministic AI audit and verification. Addresses the verification layer of AI security.
- **Bubble** (this project) — Open-source framework for studying autonomous agent behavior under containment. Addresses the behavioral layer.
- **Dooly** (internal) — Autonomous desktop agent with demonstrated UI automation, cross-application orchestration, and emergent self-replication behavior. Kept in strict isolation. Dooly assisted in building this experiment.

Together, these projects investigate a single question: **how do we build autonomous systems we can trust?**

---

## Citation

If you use this work in your research:

```
@misc{horpestad2026prisoner,
  title={The Prisoner Experiment: Behavioral Analysis of an Autonomous LLM Agent Under Containment},
  author={Horpestad, Lars O.},
  year={2026},
  publisher={AI ThinkLab AS},
  url={https://github.com/synthesis-ledger/bubble}
}
```

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

**AI ThinkLab AS** · Org.nr: 933 078 523 · Norway
Lars O. Horpestad · lars@aithinklab.com

[Full Research Paper](https://www.aithinklab.com/the-prisoner-experiment.html) · [Synthesis Ledger](https://synthesisledger.xyz) · [AI ThinkLab](https://aithinklab.com)
