# Hack Stack - Simple Docker Compose Management

# Start all services
up:
	docker compose up -d

# Stop all services
down:
	docker compose down

# Restart services
restart:
	docker compose restart

# View logs
logs:
	docker compose logs --tail=50

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