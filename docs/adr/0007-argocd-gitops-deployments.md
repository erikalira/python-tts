# 0007. Adopt Argo CD For Kubernetes GitOps Deployments

## Status

Accepted.

## Context

The repository already publishes immutable GHCR bot images and keeps optional
Kustomize overlays for staging and production. Manual deploy commands are still
useful for Docker Compose, but Kubernetes promotion should be reconciled by the
cluster from Git so drift, rollback, and review all use the same source of
truth.

## Decision

Use Argo CD as the GitOps controller for Kubernetes deployments.

- Staging follows `deploy/k8s/overlays/staging` with automated sync, prune, and
  self-heal.
- Production follows `deploy/k8s/overlays/prod` with manual sync at first.
- Image promotion is a Git change to the overlay image `newTag`.
- Rollback is a `git revert` or a new commit restoring a previous known-good
  image tag.
- Runtime secrets stay outside the public repository until a sealed-secret or
  external-secret path is adopted.

## Consequences

- Kubernetes deploys are no longer described as operator-only `kubectl apply`
  flows.
- The reviewed Git state becomes the intended cluster state.
- Production automation can be tightened later by enabling Argo CD automated
  sync after staging validation, alerting, and rollback drills are reliable.
