variable "tenancy_ocid" {
  description = "Tenancy OCID. Provide through terraform.tfvars or TF_VAR_tenancy_ocid; never commit the real value."
  type        = string
}

variable "compartment_ocid" {
  description = "Compartment OCID that will own the bot host resources."
  type        = string
}

variable "region" {
  description = "OCI region identifier, for example sa-saopaulo-1."
  type        = string
}

variable "availability_domain" {
  description = "Availability domain that hosts the instance, for example Uocm:SA-SAOPAULO-1-AD-1."
  type        = string
}

variable "name_prefix" {
  description = "Prefix applied to created resource names."
  type        = string
  default     = "python-tts"
}

variable "instance_ocpus" {
  description = "OCPUs allocated to the Ampere A1 instance."
  type        = number
  default     = 1
}

variable "instance_memory_gb" {
  description = "Memory in GB allocated to the Ampere A1 instance."
  type        = number
  default     = 6
}

variable "boot_volume_size_gb" {
  description = "Boot volume size in GB."
  type        = number
  default     = 50
}

variable "instance_image_ocid" {
  description = "Explicit Ubuntu ARM64 image OCID. Leave empty to discover the newest matching platform image."
  type        = string
  default     = ""
}

variable "ssh_public_key" {
  description = "SSH public key installed for the ubuntu user. Public key material only."
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

variable "app_dir" {
  description = "Application directory created on the instance."
  type        = string
  default     = "/opt/python-tts"
}

variable "admin_user" {
  description = "Default administrative user of the Ubuntu image."
  type        = string
  default     = "ubuntu"
}

variable "freeform_tags" {
  description = "Extra freeform tags applied to created resources."
  type        = map(string)
  default     = {}
}
