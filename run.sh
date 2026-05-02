#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

LOG="logs/run.log"
exec >>"$LOG" 2>&1

echo "=== $(date '+%F %T') start ==="

/home/liuxl/miniconda3/bin/python mplus_batch_crawler.py

bash /home/liuxl/bin/push_page.sh

echo "=== $(date '+%F %T') done ==="
