UV_PROJECT_ENVIRONMENT ?= .test-artifacts/uv-venv
PYTHONPATH ?= $(CURDIR)
CRITICAL_TESTS := tests/unit tests/contract tests/e2e tests/chaos tests/smoke

.PHONY: sync lint typecheck test security ci docker-build kustomize

sync:
	UV_PROJECT_ENVIRONMENT=$(UV_PROJECT_ENVIRONMENT) uv sync --locked --group test

lint:
	UV_PROJECT_ENVIRONMENT=$(UV_PROJECT_ENVIRONMENT) uv run --group test ruff check .

typecheck:
	UV_PROJECT_ENVIRONMENT=$(UV_PROJECT_ENVIRONMENT) uv run --group test pyright

test:
	UV_PROJECT_ENVIRONMENT=$(UV_PROJECT_ENVIRONMENT) CI=true PYTHONPATH=$(PYTHONPATH) uv run --group test pytest $(CRITICAL_TESTS) --tb=short -v

security:
	UV_PROJECT_ENVIRONMENT=$(UV_PROJECT_ENVIRONMENT) uv run --group security pip-audit

ci: lint typecheck test

docker-build:
	docker build --build-arg APP_VERSION=local --build-arg VCS_REF=$$(git rev-parse --short HEAD) -t tts-hotkey-windows-bot:local .

kustomize:
	kubectl kustomize deploy/k8s/overlays/minikube >/dev/null
	kubectl kustomize deploy/k8s/overlays/staging >/dev/null
	kubectl kustomize deploy/k8s/overlays/prod >/dev/null
