#!/bin/sh
set -e

chown -R 0:0 /app/user_data/secrets/**/*.json
python -u -m scripts.run_flow "$@"