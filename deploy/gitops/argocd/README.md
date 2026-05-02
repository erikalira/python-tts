# Argo CD GitOps

These applications make Git the deployment control plane for the Kubernetes
bot runtime.

- `staging-application.yaml` follows `deploy/k8s/overlays/staging` and enables
  automated sync, prune, and self-heal.
- `prod-application.yaml` follows `deploy/k8s/overlays/prod` and starts with
  manual sync plus self-heal guidance in the runbooks.

Before syncing either application, create the `bot-secrets` runtime Secret in
the destination namespace outside this repository.

Promotion is a Git change to the overlay image `newTag`. Rollback is a
`git revert` or a new commit that restores the previous known-good tag.
