variable "project_id" {
  description = "GCP project ID. Provide through terraform.tfvars or TF_VAR_project_id; never commit the real value."
  type        = string
}

variable "region" {
  description = "Free Tier eligible region: us-west1, us-central1, or us-east1."
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "Zone within the region, for example us-central1-a."
  type        = string
  default     = "us-central1-a"
}

variable "name_prefix" {
  description = "Prefix applied to created resource names."
  type        = string
  default     = "python-tts"
}

variable "machine_type" {
  description = "Machine type. e2-micro is the Free Tier shape."
  type        = string
  default     = "e2-micro"
}

variable "boot_disk_size_gb" {
  description = "Boot disk size in GB, up to the 30 GB Free Tier allowance."
  type        = number
  default     = 30
}

variable "boot_disk_type" {
  description = "Boot disk type. pd-standard is the Free Tier type."
  type        = string
  default     = "pd-standard"
}

variable "boot_image" {
  description = "Boot image family or self link."
  type        = string
  default     = "ubuntu-os-cloud/ubuntu-2404-lts-amd64"
}

variable "ssh_username" {
  description = "Administrative user created on the instance."
  type        = string
  default     = "ubuntu"
}

variable "ssh_public_key" {
  description = "SSH public key for the instance user. Public key material only."
  type        = string
}

variable "ssh_allowed_cidrs" {
  description = "Source CIDR blocks allowed to reach SSH. Required, and must not be 0.0.0.0/0."
  type        = list(string)
}

variable "enable_public_https" {
  description = "Open 80/tcp and 443/tcp so the bundled Caddy proxy can serve /speak over TLS."
  type        = bool
  default     = false
}

variable "public_hostname" {
  description = "Public DNS name pointed at the instance public IP. Required when enable_public_https is true."
  type        = string
  default     = ""
}

variable "bot_http_allowed_cidrs" {
  description = "Opt-in CIDRs allowed to reach the bot HTTP port directly. Keep empty in normal operation."
  type        = list(string)
  default     = []
}

variable "use_static_ip" {
  description = "Reserve a static external IP. GCP bills every public IPv4 address; a static one costs more and keeps billing while reserved. Enable only once DNS points at it."
  type        = bool
  default     = false
}

variable "app_dir" {
  description = "Application directory created on the instance."
  type        = string
  default     = "/opt/python-tts"
}

variable "labels" {
  description = "Extra labels applied to created resources."
  type        = map(string)
  default     = {}
}
