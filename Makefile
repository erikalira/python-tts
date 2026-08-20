UV_PROJECT_ENVIRONMENT ?= .test-artifacts/uv-venv
PYTHONPATH ?= $(CURDIR)
CRITICAL_TESTS := tests/unit tests/contract tests/e2e tests/chaos tests/smoke

.PHONY: sync lint typecheck test security ci docker-build docker-build-arm64 kustomize compose-config shellcheck

sync:
	UV_PROJECT_ENVIRONMENT=$(UV_PROJECT_ENVIRONMENT) uv sync --locked --group test

lint:
	UV_PROJECT_ENVIRONMENT=$(UV_PROJECT_ENVIRONMENT) uv run --group test ruff check .

typecheck:
	UV_PROJECT_ENVIRONMENT=$(UV_PROJECT_ENVIRONMENT) uv run --group test pyright

test:
	UV_PROJECT_ENVIRONMENT=$(UV_PROJECT_ENVIRONMENT) CI=true PYTHONPATH=$(PYTHONPATH) uv run --group test pytest $(CRITICAL_TESTS) --tb=short -v

# PYSEC-2026-2132: click<8.3.3 is pinned by gtts 2.5.4 and is not reachable
# from this project. See .github/workflows/security.yml for the full rationale.
security:
	UV_PROJECT_ENVIRONMENT=$(UV_PROJECT_ENVIRONMENT) uv run --group security pip-audit --ignore-vuln PYSEC-2026-2132

ci: lint typecheck test

docker-build:
	docker build --build-arg APP_VERSION=local --build-arg VCS_REF=$$(git rev-parse --short HEAD) -t tts-hotkey-windows-bot:local .

docker-build-arm64:
	docker buildx build --platform linux/arm64 --build-arg APP_VERSION=local \
		--build-arg VCS_REF=$$(git rev-parse --short HEAD) \
		-t tts-hotkey-windows-bot:local-arm64 --load .

kustomize:
	kubectl kustomize deploy/k8s/overlays/minikube >/dev/null
	kubectl kustomize deploy/k8s/overlays/staging >/dev/null
	kubectl kustomize deploy/k8s/overlays/prod >/dev/null

compose-config:
	docker compose --env-file .env.prod.example -f docker-compose.prod.yml config >/dev/null
	@echo "docker-compose.prod.yml is valid."

shellcheck:
	docker run --rm -v "$(CURDIR):/mnt" -w /mnt koalaman/shellcheck:stable \
		scripts/deploy/oci-deploy.sh scripts/deploy/oci-bootstrap-env.sh
