#!/usr/bin/env bash
set -euo pipefail
SESSION="space++"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PID_FILE="/tmp/spacepp-${UID}.pid"
if ! command -v tmux >/dev/null 2>&1; then echo "tmux not found" >&2; exit 1; fi

if [[ -f "$PID_FILE" ]]; then
    pid="$(<"$PID_FILE")"
    if [[ "$pid" =~ ^[0-9]+$ ]] && kill -0 "$pid" 2>/dev/null; then
        command_line="$(ps -p "$pid" -o command= 2>/dev/null || true)"
        if [[ "$command_line" == *"main.py"* ]]; then
            kill "$pid"
            for _ in {1..20}; do
                kill -0 "$pid" 2>/dev/null || break
                sleep 0.1
            done
            if kill -0 "$pid" 2>/dev/null; then kill -9 "$pid"; fi
        else
            echo "Refusing to stop PID $pid because it is not Space++" >&2
        fi
    fi
    rm -f "$PID_FILE"
fi

tmux has-session -t="$SESSION" 2>/dev/null || tmux new-session -d -s "$SESSION" -c "$PROJECT_DIR"
if command -v uv >/dev/null 2>&1; then CMD="uv run -p 3.12 python main.py"; elif command -v python3 >/dev/null 2>&1; then CMD="python3 main.py"; else CMD="python main.py"; fi
tmux send-keys -t "$SESSION" C-c
tmux send-keys -t "$SESSION" C-u
tmux send-keys -t "$SESSION" "cd \"$PROJECT_DIR\"" C-m
tmux send-keys -t "$SESSION" "clear" C-m
tmux send-keys -t "$SESSION" "echo \$\$ > \"$PID_FILE\"; exec $CMD" C-m
