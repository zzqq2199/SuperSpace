#!/usr/bin/env bash
set -e
SESSION="space++"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if ! command -v tmux >/dev/null 2>&1; then echo "tmux not found" >&2; exit 1; fi
ps -ef|grep python|grep space++|grep main.py|awk '{print $2}'|xargs kill -9
tmux has-session -t="$SESSION" 2>/dev/null || tmux new-session -d -s "$SESSION" -c "$PROJECT_DIR"
if command -v uv >/dev/null 2>&1; then CMD="uv run -p 3.12 python main.py"; elif command -v python3 >/dev/null 2>&1; then CMD="python3 main.py"; else CMD="python main.py"; fi
tmux send-keys -t "$SESSION" C-c
tmux send-keys -t "$SESSION" C-u
tmux send-keys -t "$SESSION" "cd \"$PROJECT_DIR\"" C-m
tmux send-keys -t "$SESSION" "clear" C-m
tmux send-keys -t "$SESSION" "$CMD" C-m
