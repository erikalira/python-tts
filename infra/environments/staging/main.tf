module "environment_contract" {
  source = "../../modules/environment_contract"

  environment_name   = "staging"
  runtime_baseline   = "production compose stack or chosen deploy target"
  release_source     = "immutable GHCR image tag"
  compute_target     = "staging deploy target"
  postgres_required  = true
  redis_required     = true
  observability_mode = "staging metrics, logs, and traces"
  kubernetes_mode    = "optional minikube validation or k3s rehearsal"
}
