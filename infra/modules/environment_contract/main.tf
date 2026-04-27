locals {
  required_services = compact([
    var.postgres_required ? "postgres" : "",
    var.redis_required ? "redis" : "",
  ])

  summary = {
    environment_name   = var.environment_name
    runtime_baseline   = var.runtime_baseline
    release_source     = var.release_source
    compute_target     = var.compute_target
    required_services  = local.required_services
    observability_mode = var.observability_mode
    kubernetes_mode    = var.kubernetes_mode
  }
}
