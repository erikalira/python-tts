module "environment_contract" {
  source = "../../modules/environment_contract"

  environment_name   = "dev"
  runtime_baseline   = "uv plus docker compose"
  release_source     = "local working tree"
  compute_target     = "developer workstation"
  postgres_required  = false
  redis_required     = false
  observability_mode = "optional local compose"
  kubernetes_mode    = "none"
}
