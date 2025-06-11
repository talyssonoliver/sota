#!/usr/bin/env bash
set -e
source "$(dirname "$0")/utils.sh"

COMPOSE="docker-compose -f docker-compose.dev.yml"

case "$1" in
  start)
    check_docker
    $COMPOSE up -d
    ;;
  stop)
    $COMPOSE down
    ;;
  restart)
    $COMPOSE restart
    ;;
  status)
    $COMPOSE ps
    ;;
  logs)
    $COMPOSE logs -f ${2:-sota-app}
    ;;
  shell)
    $COMPOSE exec sota-app bash
    ;;
  reset)
    $COMPOSE down -v
    ;;
  backup)
    bash .git/hooks/post-commit
    ;;
  *)
    echo "Usage: $0 {start|stop|restart|status|logs|shell|reset|backup}"
    exit 1
    ;;
esac
