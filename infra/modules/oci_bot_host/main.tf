# Single-node Docker host for the Discord bot on OCI Ampere A1.
#
# Scope rule: this module owns infrastructure only. Application secrets
# (DISCORD_TOKEN, BOT_SPEAK_TOKEN) are installed on the instance out of band by
# scripts/deploy/oci-bootstrap-env.sh so they never enter OpenTofu state.

locals {
  # Discovery keeps the newest patched Ubuntu ARM64 image without pinning an
  # OCID that goes stale. An explicit OCID stays available as an escape hatch
  # when a tenancy needs a reproducible image.
  discovered_image_ocid = try(data.oci_core_images.ubuntu_arm64.images[0].id, "")
  image_ocid            = var.instance_image_ocid != "" ? var.instance_image_ocid : local.discovered_image_ocid

  https_enabled = var.enable_public_https && var.public_hostname != ""

  common_tags = merge(
    {
      "project"    = "python-tts"
      "component"  = "discord-bot"
      "managed-by" = "opentofu"
    },
    var.freeform_tags,
  )
}

check "image_resolution" {
  assert {
    condition     = local.image_ocid != ""
    error_message = "No matching ARM64 platform image was found. Set instance_image_ocid explicitly, or adjust operating_system_version."
  }
}

check "https_configuration" {
  assert {
    condition     = !var.enable_public_https || var.public_hostname != ""
    error_message = "enable_public_https requires public_hostname so the reverse proxy can request a certificate for a real name."
  }
}

data "oci_core_images" "ubuntu_arm64" {
  compartment_id           = var.compartment_ocid
  operating_system         = var.operating_system
  operating_system_version = var.operating_system_version
  shape                    = var.instance_shape
  sort_by                  = "TIMECREATED"
  sort_order               = "DESC"
}

resource "oci_core_vcn" "bot" {
  compartment_id = var.compartment_ocid
  cidr_blocks    = [var.vcn_cidr]
  display_name   = "${var.name_prefix}-vcn"
  dns_label      = replace(var.name_prefix, "-", "")
  freeform_tags  = local.common_tags
}

resource "oci_core_internet_gateway" "bot" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.bot.id
  display_name   = "${var.name_prefix}-igw"
  enabled        = true
  freeform_tags  = local.common_tags
}

resource "oci_core_route_table" "bot" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.bot.id
  display_name   = "${var.name_prefix}-rt"
  freeform_tags  = local.common_tags

  route_rules {
    destination       = "0.0.0.0/0"
    destination_type  = "CIDR_BLOCK"
    network_entity_id = oci_core_internet_gateway.bot.id
    description       = "Outbound access for Discord, GHCR, and TTS providers."
  }
}

resource "oci_core_subnet" "bot" {
  compartment_id             = var.compartment_ocid
  vcn_id                     = oci_core_vcn.bot.id
  cidr_block                 = var.subnet_cidr
  display_name               = "${var.name_prefix}-public-subnet"
  dns_label                  = "public"
  route_table_id             = oci_core_route_table.bot.id
  prohibit_public_ip_on_vnic = false
  freeform_tags              = local.common_tags
}

resource "oci_core_network_security_group" "bot" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.bot.id
  display_name   = "${var.name_prefix}-nsg"
  freeform_tags  = local.common_tags
}

# Outbound: the bot must reach Discord gateway/voice, GHCR, and TTS providers.
resource "oci_core_network_security_group_security_rule" "egress_all" {
  network_security_group_id = oci_core_network_security_group.bot.id
  direction                 = "EGRESS"
  protocol                  = "all"
  destination               = "0.0.0.0/0"
  destination_type          = "CIDR_BLOCK"
  description               = "Outbound to Discord, GHCR, and TTS providers."
}

resource "oci_core_network_security_group_security_rule" "ingress_ssh" {
  for_each = toset(var.ssh_allowed_cidrs)

  network_security_group_id = oci_core_network_security_group.bot.id
  direction                 = "INGRESS"
  protocol                  = "6" # TCP
  source                    = each.value
  source_type               = "CIDR_BLOCK"
  description               = "Administrative SSH from an explicitly allowed range."

  tcp_options {
    destination_port_range {
      min = 22
      max = 22
    }
  }
}

# 80/tcp exists only for the ACME HTTP-01 challenge and the redirect to HTTPS.
resource "oci_core_network_security_group_security_rule" "ingress_http" {
  count = local.https_enabled ? 1 : 0

  network_security_group_id = oci_core_network_security_group.bot.id
  direction                 = "INGRESS"
  protocol                  = "6" # TCP
  source                    = "0.0.0.0/0"
  source_type               = "CIDR_BLOCK"
  description               = "ACME HTTP-01 challenge and redirect to HTTPS."

  tcp_options {
    destination_port_range {
      min = 80
      max = 80
    }
  }
}

resource "oci_core_network_security_group_security_rule" "ingress_https" {
  count = local.https_enabled ? 1 : 0

  network_security_group_id = oci_core_network_security_group.bot.id
  direction                 = "INGRESS"
  protocol                  = "6" # TCP
  source                    = "0.0.0.0/0"
  source_type               = "CIDR_BLOCK"
  description               = "Public HTTPS for the Desktop App /speak call, still gated by BOT_SPEAK_TOKEN."

  tcp_options {
    destination_port_range {
      min = 443
      max = 443
    }
  }
}

# Opt-in only. The default deployment keeps the bot port unreachable from the
# internet and relies on HTTPS through the proxy or an SSH tunnel.
resource "oci_core_network_security_group_security_rule" "ingress_bot_http" {
  for_each = toset(var.bot_http_allowed_cidrs)

  network_security_group_id = oci_core_network_security_group.bot.id
  direction                 = "INGRESS"
  protocol                  = "6" # TCP
  source                    = each.value
  source_type               = "CIDR_BLOCK"
  description               = "Opt-in direct access to the bot HTTP port from an allowlisted range."

  tcp_options {
    destination_port_range {
      min = var.bot_http_port
      max = var.bot_http_port
    }
  }
}

resource "oci_core_instance" "bot" {
  compartment_id      = var.compartment_ocid
  availability_domain = var.availability_domain
  display_name        = "${var.name_prefix}-bot"
  shape               = var.instance_shape
  freeform_tags       = local.common_tags

  shape_config {
    ocpus         = var.instance_ocpus
    memory_in_gbs = var.instance_memory_gb
  }

  source_details {
    source_type             = "image"
    source_id               = local.image_ocid
    boot_volume_size_in_gbs = var.boot_volume_size_gb
  }

  create_vnic_details {
    subnet_id              = oci_core_subnet.bot.id
    nsg_ids                = [oci_core_network_security_group.bot.id]
    assign_public_ip       = true
    hostname_label         = var.name_prefix
    skip_source_dest_check = false
  }

  metadata = {
    ssh_authorized_keys = trimspace(var.ssh_public_key)
    user_data           = var.cloud_init_user_data
  }

  # The boot volume carries only the OS and the runtime configuration
  # directory. Replacing the instance is expected to be recoverable by
  # re-running the bootstrap and deploy scripts.
  preserve_boot_volume = false

  lifecycle {
    ignore_changes = [
      # Platform image updates should not silently recreate a running bot host.
      source_details[0].source_id,
    ]
  }
}
