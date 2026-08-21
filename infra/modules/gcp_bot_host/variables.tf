variable "project_id" {
  description = "GCP project that owns every resource created by this module."
  type        = string

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{4,28}[a-z0-9]$", var.project_id))
    error_message = "project_id must be a valid GCP project ID."
  }
}

variable "region" {
  description = "Region for the instance. Only us-west1, us-central1, and us-east1 qualify for the Free Tier e2-micro allowance."
  type        = string
  default     = "us-central1"

  validation {
    condition     = contains(["us-west1", "us-central1", "us-east1"], var.region)
    error_message = "region must be us-west1, us-central1, or us-east1. Other regions do not qualify for the Free Tier e2-micro allowance and will be billed."
  }
}

variable "zone" {
  description = "Zone within the region, for example us-central1-a."
  type        = string
}

variable "name_prefix" {
  description = "Prefix applied to every created resource name."
  type        = string
  default     = "python-tts"

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{1,24}$", var.name_prefix))
    error_message = "name_prefix must be lowercase alphanumeric with hyphens, 2 to 25 characters."
  }
}

variable "machine_type" {
  description = "Machine type. e2-micro is the only shape covered by the Free Tier allowance."
  type        = string
  default     = "e2-micro"

  validation {
    condition     = contains(["e2-micro", "e2-small", "e2-medium"], var.machine_type)
    error_message = "machine_type must be e2-micro, e2-small, or e2-medium. Only e2-micro is covered by the Free Tier; the others are billed."
  }
}

variable "boot_disk_size_gb" {
  description = "Boot disk size in GB. The Free Tier covers 30 GB of standard persistent disk across the project."
  type        = number
  default     = 30

  validation {
    condition     = var.boot_disk_size_gb >= 10 && var.boot_disk_size_gb <= 30
    error_message = "boot_disk_size_gb must be between 10 and 30. Exceeding 30 GB goes beyond the Free Tier standard persistent disk allowance."
  }
}

variable "boot_disk_type" {
  description = "Boot disk type. Only pd-standard counts toward the Free Tier allowance."
  type        = string
  default     = "pd-standard"

  validation {
    condition     = contains(["pd-standard", "pd-balanced", "pd-ssd"], var.boot_disk_type)
    error_message = "boot_disk_type must be pd-standard, pd-balanced, or pd-ssd. Only pd-standard is covered by the Free Tier."
  }
}

variable "boot_image" {
  description = "Image family or self link for the boot disk. Defaults to the current Ubuntu 24.04 LTS amd64 family, which tracks the newest patched image."
  type        = string
  default     = "ubuntu-os-cloud/ubuntu-2404-lts-amd64"
}

variable "ssh_username" {
  description = "Linux user created on the instance and granted the SSH key."
  type        = string
  default     = "ubuntu"
}

variable "ssh_public_key" {
  description = "SSH public key for the instance user. This is a public key, not a secret."
  type        = string

  validation {
    condition     = can(regex("^(ssh-ed25519|ssh-rsa|ecdsa-sha2-nistp[0-9]+) ", trimspace(var.ssh_public_key)))
    error_message = "ssh_public_key must be an OpenSSH public key. Never pass a private key here."
  }
}

variable "ssh_allowed_cidrs" {
  description = "Source CIDR blocks allowed to reach SSH. There is no default: least privilege requires an explicit administrative range."
  type        = list(string)

  validation {
    condition     = length(var.ssh_allowed_cidrs) > 0
    error_message = "ssh_allowed_cidrs must list at least one CIDR. Leaving SSH unrestricted is not supported."
  }

  validation {
    condition     = !contains(var.ssh_allowed_cidrs, "0.0.0.0/0")
    error_message = "ssh_allowed_cidrs must not contain 0.0.0.0/0. Use the administrator's own address range instead."
  }
}

variable "enable_public_https" {
  description = "Open 80/tcp and 443/tcp so the bundled reverse proxy can terminate TLS for the /speak endpoint."
  type        = bool
  default     = false
}

variable "public_hostname" {
  description = "Public DNS hostname pointed at the instance public IP. Required when enable_public_https is true."
  type        = string
  default     = ""

  validation {
    condition     = var.public_hostname == "" || can(regex("^[a-z0-9]([a-z0-9-]*[a-z0-9])?(\\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)+$", var.public_hostname))
    error_message = "public_hostname must be an empty string or a lowercase fully qualified domain name."
  }
}

variable "bot_http_allowed_cidrs" {
  description = "Opt-in source CIDRs allowed to reach the bot HTTP port directly. Keep this empty and use HTTPS or an SSH tunnel instead."
  type        = list(string)
  default     = []

  validation {
    condition     = !contains(var.bot_http_allowed_cidrs, "0.0.0.0/0")
    error_message = "bot_http_allowed_cidrs must not contain 0.0.0.0/0. The bot HTTP port must never be open to the whole internet."
  }
}

variable "bot_http_port" {
  description = "Port the bot container listens on inside the host network."
  type        = number
  default     = 10000
}

variable "subnet_cidr" {
  description = "CIDR block for the subnet."
  type        = string
  default     = "10.30.1.0/24"
}

variable "cloud_init_user_data" {
  description = "cloud-init user data. Must not contain application secrets: instance metadata is readable from the instance and is stored in state."
  type        = string
}

variable "labels" {
  description = "Labels applied to created resources."
  type        = map(string)
  default     = {}
}
