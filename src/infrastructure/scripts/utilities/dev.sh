#!/bin/bash
# SOTA Development Management Script
# Location: scripts/dev.sh
# Usage: ./scripts/dev.sh [command] [options]
# Make executable: chmod +x scripts/dev.sh

set -e

# Colors and formatting
readonly RED="\033[0;31m"
readonly GREEN="\033[0;32m"
readonly YELLOW="\033[1;33m"
readonly BLUE="\033[0;34m"
readonly PURPLE="\033[0;35m"
readonly CYAN="\033[0;36m"
readonly NC="\033[0m"
readonly BOLD="\033[1m"

# Configuration
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
readonly COMPOSE_FILE="docker-compose.dev.yml"
readonly LOG_DIR=".sota_logs"
readonly HEALTH_CHECK_TIMEOUT=60

# Utility functions
log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }
log_debug() { [[ "${DEBUG:-}" == "1" ]] && echo -e "${PURPLE}🐛 $1${NC}"; }

# Progress bar function
show_progress() {
    local current=$1
    local total=$2
    local task=$3
    local width=30
    local progress=$((current * width / total))
    printf "\r${CYAN}[$current/$total] $task "
    printf '█%.0s' $(seq 1 $progress)
    printf '░%.0s' $(seq $((progress + 1)) $width)
    printf "${NC}"
    [[ $current -eq $total ]] && echo ""
}

# Check prerequisites
check_prerequisites() {
    local missing=()
    command -v docker >/dev/null 2>&1 || missing+=("docker")
    command -v docker-compose >/dev/null 2>&1 || missing+=("docker-compose")
    if [[ ${#missing[@]} -gt 0 ]]; then
        log_error "Missing required tools: ${missing[*]}"
        log_info "Please install missing tools and try again"
        return 1
    fi
    if ! docker info >/dev/null 2>&1; then
        log_error "Docker is not running. Please start Docker and try again"
        return 1
    fi
}

get_service_status() {
    local service=$1
    docker-compose -f "$COMPOSE_FILE" ps -q "$service" 2>/dev/null | head -1
}

is_service_healthy() {
    local service=$1
    local container_id=$(get_service_status "$service")
    [[ -z "$container_id" ]] && return 1
    local health=$(docker inspect --format='{{.State.Health.Status}}' "$container_id" 2>/dev/null || echo "none")
    [[ "$health" == "healthy" ]] || [[ "$health" == "none" ]]
}

wait_for_service() {
    local service=$1
    local timeout=${2:-$HEALTH_CHECK_TIMEOUT}
    local elapsed=0
    log_info "Waiting for $service to be healthy..."
    while [[ $elapsed -lt $timeout ]]; do
        if is_service_healthy "$service"; then
            log_success "$service is healthy"
            return 0
        fi
        show_progress $elapsed $timeout "Waiting for $service"
        sleep 2
        elapsed=$((elapsed + 2))
    done
    log_error "$service failed to become healthy within ${timeout}s"
    return 1
}

detect_changed_services() {
    local changed_files
    changed_files=$(git diff --name-only HEAD~1 HEAD 2>/dev/null || echo "")
    local services=()
    if echo "$changed_files" | grep -qE '\.(py|yml|yaml|toml|txt)$'; then
        services+=("sota-app")
    fi
    if echo "$changed_files" | grep -qE 'Dockerfile|docker-compose'; then
        services+=("sota-app" "chroma" "redis")
    fi
    if echo "$changed_files" | grep -q 'config/'; then
        services+=("redis" "docs")
    fi
    printf '%s\n' "${services[@]}" | sort -u
}

cmd_start() {
    local services=("$@")
    log_info "Starting SOTA development environment..."
    check_prerequisites || return 1
    mkdir -p "$LOG_DIR"
    if [[ ${#services[@]} -eq 0 ]]; then
        docker-compose -f "$COMPOSE_FILE" up -d
        wait_for_service "chroma" 30
        wait_for_service "redis" 15
        wait_for_service "sota-app" 45
    else
        docker-compose -f "$COMPOSE_FILE" up -d "${services[@]}"
        for service in "${services[@]}"; do
            wait_for_service "$service"
        done
    fi
    log_success "Development environment started!"
    cmd_status
}

cmd_stop() {
    local services=("$@")
    log_info "Stopping SOTA development services..."
    if [[ ${#services[@]} -eq 0 ]]; then
        docker-compose -f "$COMPOSE_FILE" down
        log_success "All services stopped"
    else
        docker-compose -f "$COMPOSE_FILE" stop "${services[@]}"
        log_success "Services stopped: ${services[*]}"
    fi
}

cmd_restart() {
    local services=("$@")
    if [[ ${#services[@]} -eq 0 ]]; then
        local changed_services
        mapfile -t changed_services < <(detect_changed_services)
        if [[ ${#changed_services[@]} -gt 0 ]]; then
            log_info "Restarting changed services: ${changed_services[*]}"
            docker-compose -f "$COMPOSE_FILE" restart "${changed_services[@]}"
        else
            log_info "No changes detected, restarting all services"
            docker-compose -f "$COMPOSE_FILE" restart
        fi
    else
        log_info "Restarting services: ${services[*]}"
        docker-compose -f "$COMPOSE_FILE" restart "${services[@]}"
    fi
    log_success "Services restarted"
    cmd_status
}

cmd_status() {
    log_info "SOTA Development Environment Status"
    echo ""
    printf "%-15s %-10s %-10s %-20s\n" "SERVICE" "STATUS" "HEALTH" "PORTS"
    printf "%-15s %-10s %-10s %-20s\n" "-------" "------" "------" "-----"
    local services=("sota-app" "chroma" "redis" "docs" "postgres" "jupyter")
    for service in "${services[@]}"; do
        local cid=$(get_service_status "$service")
        local status="stopped"
        local health="n/a"
        local ports="n/a"
        if [[ -n "$cid" ]]; then
            status=$(docker inspect --format='{{.State.Status}}' "$cid" 2>/dev/null || echo "unknown")
            health=$(docker inspect --format='{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' "$cid" 2>/dev/null || echo "none")
            ports=$(docker port "$cid" 2>/dev/null | tr '\n' ' ' || echo "none")
        fi
        local color=""
        case $status in
            running) color="$GREEN" ;;
            stopped|exited) color="$RED" ;;
            *) color="$YELLOW" ;;
        esac
        printf "%-15s ${color}%-10s${NC} %-10s %-20s\n" "$service" "$status" "$health" "$ports"
    done
    echo ""
    log_info "Resource Usage"
    docker-compose -f "$COMPOSE_FILE" top 2>/dev/null || log_warning "Could not retrieve resource usage"
}

cmd_logs() {
    local service=${1:-}
    local options=()
    shift || true
    while [[ $# -gt 0 ]]; do
        case $1 in
            -f|--follow) options+=("--follow") ;;
            -t|--tail) options+=("--tail" "$2"); shift ;;
            --since) options+=("--since" "$2"); shift ;;
            *) log_warning "Unknown option: $1" ;;
        esac
        shift
    done
    if [[ -z "$service" ]]; then
        log_info "Showing logs for all services..."
        docker-compose -f "$COMPOSE_FILE" logs "${options[@]}"
    else
        log_info "Showing logs for $service..."
        docker-compose -f "$COMPOSE_FILE" logs "${options[@]}" "$service"
    fi
}

cmd_shell() {
    local service=${1:-sota-app}
    local shell=${2:-bash}
    log_info "Opening shell in $service container..."
    docker-compose -f "$COMPOSE_FILE" exec "$service" "$shell" || {
        log_warning "Could not open $shell, trying sh..."
        docker-compose -f "$COMPOSE_FILE" exec "$service" sh
    }
}

cmd_reset() {
    log_warning "This will completely reset the development environment!"
    read -p "Are you sure? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Resetting development environment..."
        docker-compose -f "$COMPOSE_FILE" down --volumes --remove-orphans
        docker volume rm sota-chroma-data sota-redis-data sota-docs-build 2>/dev/null || true
        rm -rf "$LOG_DIR"
        log_success "Environment reset completed"
        log_info "Run './scripts/dev.sh start' to restart"
    else
        log_info "Reset cancelled"
    fi
}

cmd_backup() {
    local backup_name="dev_backup_$(date +%Y%m%d_%H%M%S)"
    local backup_dir=".sota_backups"
    mkdir -p "$backup_dir"
    log_info "Creating development backup: $backup_name"
    docker-compose -f "$COMPOSE_FILE" run --rm \
        -v "sota-chroma-data:/backup/chroma" \
        -v "sota-redis-data:/backup/redis" \
        -v "$PWD/$backup_dir:/output" \
        busybox tar czf "/output/${backup_name}.tar.gz" -C /backup .
    log_success "Backup created: $backup_dir/${backup_name}.tar.gz"
}

cmd_debug_agent() {
    local agent_name=${1:-}
    if [[ -z "$agent_name" ]]; then
        log_error "Please specify agent name"
        return 1
    fi
    log_info "Starting debug session for $agent_name agent..."
    docker-compose -f "$COMPOSE_FILE" exec sota-app python -m debugpy --listen 0.0.0.0:5678 --wait-for-client "agents/${agent_name}_agent.py"
}

cmd_test_workflow() {
    log_info "Testing LangGraph workflows..."
    docker-compose -f "$COMPOSE_FILE" exec sota-app python scripts/test_workflows.py
}

cmd_metrics() {
    log_info "System Performance Metrics"
    echo ""
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}" $(docker-compose -f "$COMPOSE_FILE" ps -q) 2>/dev/null || log_warning "Could not retrieve metrics"
}

cmd_help() {
    cat <<HELP
${BOLD}${BLUE}SOTA Development Management Script${NC}

${GREEN}Usage:${NC}
  ./scripts/dev.sh [command] [options]

${GREEN}Commands:${NC}
  ${YELLOW}start [services...]${NC}     Start development environment
  ${YELLOW}stop [services...]${NC}      Stop services
  ${YELLOW}restart [services...]${NC}   Restart services (smart restart if no services specified)
  ${YELLOW}status${NC}                  Show comprehensive status
  ${YELLOW}logs [service] [options]${NC} Show logs (use -f to follow, -t N for tail)
  ${YELLOW}shell [service] [shell]${NC}  Interactive shell (default: sota-app, bash)
  ${YELLOW}reset${NC}                   Complete environment reset
  ${YELLOW}backup${NC}                  Create development backup
  ${YELLOW}metrics${NC}                 Show performance metrics
  ${YELLOW}debug-agent <name>${NC}      Debug specific agent
  ${YELLOW}test-workflow${NC}           Test LangGraph workflows
  ${YELLOW}help${NC}                    Show this help

${GREEN}Examples:${NC}
  ./scripts/dev.sh start                    # Start all services
  ./scripts/dev.sh start sota-app chroma    # Start specific services
  ./scripts/dev.sh logs sota-app -f         # Follow logs for main app
  ./scripts/dev.sh shell redis              # Open shell in Redis container
  ./scripts/dev.sh debug-agent researcher   # Debug researcher agent

${GREEN}Environment Variables:${NC}
  DEBUG=1                                   # Enable debug output
  COMPOSE_FILE=custom.yml                   # Use custom compose file
HELP
}

main() {
    cd "$PROJECT_ROOT"
    local command=${1:-help}
    shift || true
    case $command in
        start) cmd_start "$@" ;;
        stop) cmd_stop "$@" ;;
        restart) cmd_restart "$@" ;;
        status) cmd_status ;;
        logs) cmd_logs "$@" ;;
        shell) cmd_shell "$@" ;;
        reset) cmd_reset ;;
        backup) cmd_backup ;;
        metrics) cmd_metrics ;;
        debug-agent) cmd_debug_agent "$@" ;;
        test-workflow) cmd_test_workflow ;;
        help|--help|-h) cmd_help ;;
        *) log_error "Unknown command: $command"; echo ""; cmd_help; exit 1 ;;
    esac
}

main "$@"
