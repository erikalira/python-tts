# Single-node Docker host for the Discord bot on GCP Compute Engine.
#
# This is the fallback target for when OCI Ampere A1 capacity is unavailable.
# It is smaller than the OCI host (1 GB vs 6 GB), so the compose definition
# caps container memory; see docker-compose.vm.yml.
#
# Scope rule: this module owns infrastructure only. Application secrets
# (DISCORD_TOKEN, BOT_SPEAK_TOKEN) are installed on the instance out of band by
# scripts/deploy/vm-bootstrap-env.sh so they never enter OpenTofu state.

locals {
  https_enabled = var.enable_public_https && var.public_hostname != ""

  common_labels = merge(
    {
      "project"    = "python-tts"
      "component"  = "discord-bot"
      "managed-by" = "opentofu"
    },
    var.labels,
  )

  # Network tags drive firewall rule targeting. Each rule applies only to
  # instances carrying its tag, so nothing else in the project is exposed.
  ssh_tag       = "${var.name_prefix}-ssh"
  https_tag     = "${var.name_prefix}-https"
  bot_http_tag  = "${var.name_prefix}-bot-http"
  instance_tags = compact([local.ssh_tag, local.https_enabled ? local.https_tag : "", length(var.bot_http_allowed_cidrs) > 0 ? local.bot_http_tag : ""])
}

check "https_configuration" {
  assert {
    condition     = !var.enable_public_https || var.public_hostname != ""
    error_message = "enable_public_https requires public_hostname so the reverse proxy can request a certificate for a real name."
  }
}

check "free_tier_shape" {
  assert {
    condition     = var.machine_type == "e2-micro"
    error_message = "machine_type is not e2-micro, so this instance is billed rather than covered by the Free Tier allowance. Confirm this is intentional."
  }
}

resource "google_compute_network" "bot" {
  name                    = "${var.name_prefix}-vpc"
  project                 = var.project_id
  auto_create_subnetworks = false
  description             = "Network for the python-tts Discord bot host."
}

resource "google_compute_subnetwork" "bot" {
  name          = "${var.name_prefix}-subnet"
  project       = var.project_id
  region        = var.region
  network       = google_compute_network.bot.id
  ip_cidr_range = var.subnet_cidr

  # Flow logs bill by volume and add nothing for a single-node host.
  private_ip_google_access = false
}

resource "google_compute_firewall" "ssh" {
  name    = "${var.name_prefix}-allow-ssh"
  project = var.project_id
  network = google_compute_network.bot.name

  description   = "Administrative SSH from an explicitly allowed range."
  direction     = "INGRESS"
  source_ranges = var.ssh_allowed_cidrs
  target_tags   = [local.ssh_tag]

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }
}

# 80/tcp exists only for the ACME HTTP-01 challenge and the redirect to HTTPS.
resource "google_compute_firewall" "https" {
  count = local.https_enabled ? 1 : 0

  name    = "${var.name_prefix}-allow-https"
  project = var.project_id
  network = google_compute_network.bot.name

  description   = "Public HTTPS for the Desktop App /speak call, still gated by BOT_SPEAK_TOKEN, plus ACME on 80."
  direction     = "INGRESS"
  source_ranges = ["0.0.0.0/0"]
  target_tags   = [local.https_tag]

  allow {
    protocol = "tcp"
    ports    = ["80", "443"]
  }
}

# Opt-in only. The default deployment keeps the bot port unreachable from the
# internet and relies on HTTPS through the proxy or an SSH tunnel.
resource "google_compute_firewall" "bot_http" {
  count = length(var.bot_http_allowed_cidrs) > 0 ? 1 : 0

  name    = "${var.name_prefix}-allow-bot-http"
  project = var.project_id
  network = google_compute_network.bot.name

  description   = "Opt-in direct access to the bot HTTP port from an allowlisted range."
  direction     = "INGRESS"
  source_ranges = var.bot_http_allowed_cidrs
  target_tags   = [local.bot_http_tag]

  allow {
    protocol = "tcp"
    ports    = [tostring(var.bot_http_port)]
  }
}

# GCP denies ingress by default, so no explicit deny rule is needed. Egress is
# allowed by default, which the bot needs for Discord, GHCR, and TTS providers.

resource "google_compute_address" "bot" {
  name         = "${var.name_prefix}-ip"
  project      = var.project_id
  region       = var.region
  address_type = "EXTERNAL"

  # A static address survives instance recreation, so the DNS record and the
  # deployment secrets do not need updating after a rebuild.
  description = "Static public IP for the python-tts bot host."
}

resource "google_compute_instance" "bot" {
  name         = "${var.name_prefix}-bot"
  project      = var.project_id
  zone         = var.zone
  machine_type = var.machine_type
  labels       = local.common_labels
  tags         = local.instance_tags

  boot_disk {
    initialize_params {
      image = var.boot_image
      size  = var.boot_disk_size_gb
      type  = var.boot_disk_type
    }
  }

  network_interface {
    subnetwork = google_compute_subnetwork.bot.id

    access_config {
      nat_ip = google_compute_address.bot.address
    }
  }

  metadata = {
    # OS Login is disabled so the key below is the single documented access
    # path, matching how the OCI target works.
    enable-oslogin = "FALSE"
    ssh-keys       = "${var.ssh_username}:${trimspace(var.ssh_public_key)}"
    user-data      = var.cloud_init_user_data
  }

  # e2-micro is a shared-core shape; the bot tolerates a brief migration pause
  # better than an unplanned termination.
  scheduling {
    automatic_restart   = true
    on_host_maintenance = "MIGRATE"
    preemptible         = false
  }

  # No service account scopes: this host calls no Google APIs. Omitting the
  # block entirely would attach the default account with default scopes.
  service_account {
    scopes = []
  }

  allow_stopping_for_update = true

  lifecycle {
    ignore_changes = [
      # Image family updates should not silently recreate a running bot host.
      boot_disk[0].initialize_params[0].image,
    ]
  }
}
