# OCI Ampere A1 environment: a small always-on ARM64 Docker host for the
# Discord bot. This is an additional deployment target, not a replacement for
# the Docker/Postgres or Windows shapes.
#
# Secrets boundary: this environment owns infrastructure only. DISCORD_TOKEN and
# BOT_SPEAK_TOKEN are installed directly on the instance and never appear in
# variables, cloud-init, or state.

module "environment_contract" {
  source = "../../modules/environment_contract"

  environment_name   = "prod"
  runtime_baseline   = "versioned GHCR image on a single ARM64 Docker host"
  release_source     = "semantic release tag"
  compute_target     = "OCI VM.Standard.A1.Flex running Ubuntu ARM64"
  postgres_required  = false
  redis_required     = false
  observability_mode = "health and readiness endpoints only"
  kubernetes_mode    = "not used on this target"
}

module "bot_host" {
  source = "../../modules/oci_bot_host"

  compartment_ocid    = var.compartment_ocid
  availability_domain = var.availability_domain
  name_prefix         = var.name_prefix

  instance_ocpus      = var.instance_ocpus
  instance_memory_gb  = var.instance_memory_gb
  boot_volume_size_gb = var.boot_volume_size_gb
  instance_image_ocid = var.instance_image_ocid

  ssh_public_key    = var.ssh_public_key
  ssh_allowed_cidrs = var.ssh_allowed_cidrs

  enable_public_https    = var.enable_public_https
  public_hostname        = var.public_hostname
  bot_http_allowed_cidrs = var.bot_http_allowed_cidrs

  cloud_init_user_data = base64encode(templatefile("${path.module}/cloud-init.yaml.tftpl", {
    app_dir    = var.app_dir
    admin_user = var.admin_user
  }))

  freeform_tags = var.freeform_tags
}
