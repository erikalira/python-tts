# GCP e2-micro environment: the fallback single-node host for the Discord bot
# when OCI Ampere A1 capacity is unavailable.
#
# This host is materially smaller than the OCI one (1 GB vs 6 GB), so the
# runtime caps container memory and cloud-init provisions swap. Prefer the OCI
# target when capacity allows.
#
# Secrets boundary: this environment owns infrastructure only. DISCORD_TOKEN and
# BOT_SPEAK_TOKEN are installed directly on the instance and never appear in
# variables, cloud-init, or state.

module "environment_contract" {
  source = "../../modules/environment_contract"

  environment_name   = "prod"
  runtime_baseline   = "versioned GHCR image on a single amd64 Docker host"
  release_source     = "semantic release tag"
  compute_target     = "GCP e2-micro running Ubuntu 24.04 amd64"
  postgres_required  = false
  redis_required     = false
  observability_mode = "health and readiness endpoints only"
  kubernetes_mode    = "not used on this target"
}

module "bot_host" {
  source = "../../modules/gcp_bot_host"

  project_id  = var.project_id
  region      = var.region
  zone        = var.zone
  name_prefix = var.name_prefix

  machine_type      = var.machine_type
  boot_disk_size_gb = var.boot_disk_size_gb
  boot_disk_type    = var.boot_disk_type
  boot_image        = var.boot_image

  ssh_username      = var.ssh_username
  ssh_public_key    = var.ssh_public_key
  ssh_allowed_cidrs = var.ssh_allowed_cidrs

  use_static_ip = var.use_static_ip

  enable_public_https    = var.enable_public_https
  public_hostname        = var.public_hostname
  bot_http_allowed_cidrs = var.bot_http_allowed_cidrs

  cloud_init_user_data = templatefile("${path.module}/cloud-init.yaml.tftpl", {
    app_dir    = var.app_dir
    admin_user = var.ssh_username
  })

  labels = var.labels
}
