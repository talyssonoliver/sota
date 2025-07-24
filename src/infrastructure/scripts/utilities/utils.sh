#!/usr/bin/env bash

check_docker() {
  if ! command -v docker &>/dev/null; then
    echo "❌ Docker not found. Please install Docker." >&2
    exit 1
  fi
}
