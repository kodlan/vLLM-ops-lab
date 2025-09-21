
.PHONY: setup infra-up infra-down infra-logs health test-prompt

# =============================================================================
# Setup
# =============================================================================

setup:
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "Created .env from .env.example"; \
		echo "Edit .env to customize settings if needed"; \
	else \
		echo ".env already exists"; \
	fi

# =============================================================================
# Infrastructure (Base vLLM Server)
# =============================================================================

infra-up:
	docker compose --env-file .env -f infra/docker-compose.base.yml up -d
	@echo "vLLM server starting... Use 'make infra-logs' to watch progress"
	@echo "Use 'make health' to check when ready"

infra-down:
	docker compose --env-file .env -f infra/docker-compose.base.yml down

infra-logs:
	docker compose --env-file .env -f infra/docker-compose.base.yml logs -f

health:
	@curl -sf http://localhost:8000/health > /dev/null && echo "vLLM is healthy" || echo "vLLM is not ready"

test-prompt:
	@curl -s http://localhost:8000/v1/completions \
		-H "Content-Type: application/json" \
		-d '{"model": "$(MODEL_NAME)", "prompt": "Hello, I am", "max_tokens": 20}' \
		| python3 -c "import sys,json; print(json.load(sys.stdin)['choices'][0]['text'])"

# =============================================================================
# Experiment 1: Sleep Mode Router
# =============================================================================

exp1-up:
	docker compose --env-file .env -f experiments/01_sleep_mode_router/docker-compose.yml up -d
	@echo "Sleep mode server starting..."

exp1-down:
	docker compose --env-file .env -f experiments/01_sleep_mode_router/docker-compose.yml down

exp1-logs:
	docker compose --env-file .env -f experiments/01_sleep_mode_router/docker-compose.yml logs -f

exp1-demo:
	cd experiments/01_sleep_mode_router && python3 router.py --demo

exp1-sleep:
	cd experiments/01_sleep_mode_router && python3 router.py --sleep

exp1-wake:
	cd experiments/01_sleep_mode_router && python3 router.py --wake

exp1-benchmark:
	cd experiments/01_sleep_mode_router && python3 benchmark.py