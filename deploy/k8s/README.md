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

## Secret Handling

The base uses placeholder `secretGenerator` literals so `kubectl kustomize`
produces a complete manifest for validation. Do not deploy those placeholders
to shared environments. Replace them through a sealed secret, external secret
operator, CI-created Secret, or a private overlay that is not committed.

## Database Schema

The base keeps copies of the Postgres initialization SQL under
`base/postgres-initdb/` because Kustomize intentionally restricts file loading
outside the kustomization root. Keep those files aligned with
`deploy/postgres/` when schema bootstrap changes.
