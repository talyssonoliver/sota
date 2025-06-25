#!/usr/bin/env bash
set -e
source "$(dirname "$0")/utils.sh"

check_docker

docker-compose -f docker-compose.dev.yml ps
