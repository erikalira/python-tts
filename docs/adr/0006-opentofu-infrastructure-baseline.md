# ADR 0006: Use OpenTofu As The Infrastructure Baseline

## Status

Accepted

## Context

The repository already has Docker Compose files for local development,
production-like bot deployment, Postgres, Redis, and observability. That is
enough to run the application, but it does not describe the expected
environment shape in a reusable IaC model.

The project needs a clear default before adding provider-specific infrastructure
code. Choosing both OpenTofu and Terraform as equal options would split command
examples, state expectations, CI checks, and contributor habits.

## Decision

OpenTofu is the repository's default infrastructure-as-code tool. Terraform
compatibility is treated as a syntax and provider ecosystem benefit, not as a
second operating mode.

Docker Compose remains the local runtime baseline. OpenTofu will describe
environment ownership, cloud or host resources, and integration points around
the runtime, starting with placeholders for compute, secrets, Postgres, Redis,
and observability. Kubernetes remains optional; manifests may be validated with
Minikube locally, but production Kubernetes should target k3s or a small
managed cluster only after the Compose-based release path is healthy.

## Consequences

- IaC examples and validation commands use `tofu`.
- Terraform users may adapt the HCL manually, but repository automation does
  not need to support two CLIs.
- Provider-specific modules should be added only when an actual deployment
  target is chosen.
- Secrets must not be committed to `infra/`, `.tfvars`, environment examples,
  or state snapshots.
