module "environment_contract" {
  source = "../../modules/environment_contract"

  environment_name   = "prod"
  runtime_baseline   = "versioned GHCR image"
  release_source     = "semantic release tag"
  compute_target     = "production deploy target"
  postgres_required  = true
  redis_required     = true
  observability_mode = "production metrics, logs, and traces"
  kubernetes_mode    = "optional k3s or managed cluster after adoption decision"
}
