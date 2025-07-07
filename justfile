# Hack Stack - Simple Docker Compose Management

# Start all services
start:
	docker compose up -d

# Stop all services
stop:
	docker compose down

# Restart services
restart:
	docker compose restart

# View logs
logs:
	docker compose logs -f

# Check service status
status:
	docker compose ps

# Build and start (clean slate)
build:
	docker compose up --build -d

# Clean up everything
clean:
	docker compose down -v --remove-orphans
	docker system prune -f

# Quick development setup
dev:
	docker compose up --build

# Open the app in browser (after starting)
open:
	@echo "Opening app..."
	@sleep 2
	@which xdg-open >/dev/null && xdg-open http://localhost:2872 || echo "Open http://localhost:2872 in your browser"

# Complete setup: build, start, and open
demo: build open