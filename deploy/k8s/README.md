# Kubernetes Manifests

These manifests are optional. Docker Compose remains the default local and
production-like runtime path. Use Kustomize when you want to validate or rehearse
the bot stack on Kubernetes.

## Overlays

- `overlays/minikube`: local manifest validation and developer smoke testing
- `overlays/staging`: production rehearsal shape with one bot replica
- `overlays/prod`: production shape with two bot replicas and stricter resource
  requests

## Local Validation

```powershell
kubectl kustomize deploy/k8s/overlays/minikube
kubectl kustomize deploy/k8s/overlays/staging
kubectl kustomize deploy/k8s/overlays/prod
```

For Minikube, build or load an image that matches the overlay tag before
applying the manifests.

## GitOps

Argo CD applications live in `deploy/gitops/argocd/`.

- Staging reconciles `deploy/k8s/overlays/staging` automatically with prune and
  self-heal enabled.
- Production reconciles `deploy/k8s/overlays/prod` with manual sync first.
- Promote by changing the overlay image `newTag` to an immutable GHCR release
  tag.
- Roll back by reverting that Git change or committing the previous known-good
  tag.

## Secret Handling

The base references a `bot-secrets` Kubernetes Secret but does not generate it.
Create that Secret outside this public repository before applying or syncing a
shared environment.

Required keys:

- `DISCORD_TOKEN`
- `BOT_SPEAK_TOKEN`
- `POSTGRES_PASSWORD`

Use a sealed secret, external secret operator, CI-created Secret, or a private
overlay that is not committed.

## Database Schema

The base keeps copies of the Postgres initialization SQL under
`base/postgres-initdb/` because Kustomize intentionally restricts file loading
outside the kustomization root. Keep those files aligned with
`deploy/postgres/` when schema bootstrap changes.
