#!/bin/bash

# Docker Compose startup script for Flower Shop system
# Starts all services: Postgres, Redis, Backend, MCP Server, AI Agent

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🌸 Flower Shop - Docker Compose Startup${NC}"
echo "=========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Error: Docker is not installed${NC}"
    echo "Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo -e "${RED}❌ Error: Docker daemon is not running${NC}"
    echo "Please start Docker Desktop"
    exit 1
fi

echo -e "${GREEN}✅ Docker is running${NC}"
echo ""

# Check if docker-compose.yml exists
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}❌ Error: docker-compose.yml not found${NC}"
    echo "Please run this script from the project root directory"
    exit 1
fi

# Check for .env file and warn if CLAUDE_API_KEY is missing
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  Warning: .env file not found${NC}"
    echo "Creating .env template..."
    echo "CLAUDE_API_KEY=your-api-key-here" > .env
    echo -e "${YELLOW}Please edit .env and add your CLAUDE_API_KEY${NC}"
    echo ""
fi

# Parse command line arguments
MODE="${1:-up}"  # Default to "up"

case "$MODE" in
    up)
        echo -e "${BLUE}🚀 Starting all services...${NC}"
        echo ""
        docker-compose up -d
        echo ""
        echo -e "${GREEN}✅ All services started${NC}"
        echo ""
        echo -e "${BLUE}📊 Service Status:${NC}"
        docker-compose ps
        echo ""
        echo -e "${BLUE}🔗 Service URLs:${NC}"
        echo "  Backend:    http://localhost:8014"
        echo "  MCP Server: http://localhost:8001"
        echo "  AI Agent:   http://localhost:8000"
        echo "  Postgres:   localhost:5432"
        echo "  Redis:      localhost:6379"
        echo ""
        echo -e "${YELLOW}💡 Tip: Use 'docker-compose logs -f' to view live logs${NC}"
        echo -e "${YELLOW}💡 Tip: Use 'docker-compose down' to stop all services${NC}"
        echo -e "${YELLOW}💡 Tip: Use './scripts/docker-start.sh logs' to view logs${NC}"
        ;;

    down)
        echo -e "${BLUE}🛑 Stopping all services...${NC}"
        docker-compose down
        echo -e "${GREEN}✅ All services stopped${NC}"
        ;;

    restart)
        echo -e "${BLUE}🔄 Restarting all services...${NC}"
        docker-compose restart
        echo -e "${GREEN}✅ All services restarted${NC}"
        ;;

    logs)
        echo -e "${BLUE}📜 Showing logs (Ctrl+C to exit)...${NC}"
        docker-compose logs -f
        ;;

    build)
        echo -e "${BLUE}🔨 Rebuilding all services...${NC}"
        docker-compose build --no-cache
        echo -e "${GREEN}✅ All services rebuilt${NC}"
        ;;

    clean)
        echo -e "${YELLOW}🧹 Cleaning up Docker resources...${NC}"
        echo "This will remove containers, volumes, and networks"
        read -p "Are you sure? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker-compose down -v
            echo -e "${GREEN}✅ Cleanup complete${NC}"
        else
            echo "Cancelled"
        fi
        ;;

    status)
        echo -e "${BLUE}📊 Service Status:${NC}"
        docker-compose ps
        echo ""
        echo -e "${BLUE}🏥 Health Checks:${NC}"
        echo "Backend:    $(curl -sf http://localhost:8014/health > /dev/null && echo -e "${GREEN}✅ Healthy${NC}" || echo -e "${RED}❌ Unhealthy${NC}")"
        echo "MCP Server: $(curl -sf http://localhost:8001/health > /dev/null && echo -e "${GREEN}✅ Healthy${NC}" || echo -e "${RED}❌ Unhealthy${NC}")"
        echo "AI Agent:   $(curl -sf http://localhost:8000/health > /dev/null && echo -e "${GREEN}✅ Healthy${NC}" || echo -e "${RED}❌ Unhealthy${NC}")"
        ;;

    help|--help|-h)
        echo "Usage: $0 [COMMAND]"
        echo ""
        echo "Commands:"
        echo "  up       Start all services (default)"
        echo "  down     Stop all services"
        echo "  restart  Restart all services"
        echo "  logs     View live logs"
        echo "  build    Rebuild all service images"
        echo "  clean    Remove all containers, volumes, and networks"
        echo "  status   Show service status and health"
        echo "  help     Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0              # Start all services"
        echo "  $0 up           # Start all services"
        echo "  $0 logs         # View logs"
        echo "  $0 down         # Stop all services"
        ;;

    *)
        echo -e "${RED}❌ Unknown command: $MODE${NC}"
        echo "Run '$0 help' for usage information"
        exit 1
        ;;
esac
