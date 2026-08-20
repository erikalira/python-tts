variable "compartment_ocid" {
  description = "Compartment that owns every resource created by this module."
  type        = string

  validation {
    condition     = can(regex("^ocid1\\.(compartment|tenancy)\\.", var.compartment_ocid))
    error_message = "compartment_ocid must be an OCI compartment or tenancy OCID."
  }
}

variable "availability_domain" {
  description = "Availability domain name that hosts the instance, for example Uocm:PHX-AD-1."
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

variable "instance_shape" {
  description = "Compute shape for the bot host. The Ampere A1 flexible shape is the supported default."
  type        = string
  default     = "VM.Standard.A1.Flex"
}

variable "instance_ocpus" {
  description = "OCPUs allocated to the instance. Keep this small; Always Free A1 capacity is tenancy-wide."
  type        = number
  default     = 1

  validation {
    condition     = var.instance_ocpus >= 1 && var.instance_ocpus <= 4 && floor(var.instance_ocpus) == var.instance_ocpus
    error_message = "instance_ocpus must be a whole number between 1 and 4. Larger A1 instances can exceed a tenancy's Always Free allocation and start billing."
  }
}

variable "instance_memory_gb" {
  description = "Memory in GB allocated to the instance."
  type        = number
  default     = 6

  validation {
    condition     = var.instance_memory_gb >= 6 && var.instance_memory_gb <= 24
    error_message = "instance_memory_gb must be between 6 and 24. Larger A1 instances can exceed a tenancy's Always Free allocation and start billing."
  }
}

variable "boot_volume_size_gb" {
  description = "Boot volume size in GB."
  type        = number
  default     = 50

  validation {
    condition     = var.boot_volume_size_gb >= 50 && var.boot_volume_size_gb <= 200
    error_message = "boot_volume_size_gb must be between 50 and 200. OCI requires at least 50 GB, and large volumes can exceed a tenancy's Always Free block storage allocation."
  }
}

variable "operating_system" {
  description = "Operating system used to discover the platform image."
  type        = string
  default     = "Canonical Ubuntu"
}

variable "operating_system_version" {
  description = "Operating system version used to discover the platform image."
  type        = string
  default     = "24.04"
}

variable "instance_image_ocid" {
  description = "Explicit image OCID. Leave empty to discover the newest matching ARM64 platform image through the OCI provider."
  type        = string
  default     = ""
}

variable "ssh_public_key" {
  description = "SSH public key installed for the default ubuntu user. This is a public key, not a secret."
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

variable "vcn_cidr" {
  description = "CIDR block for the VCN."
  type        = string
  default     = "10.20.0.0/16"
}

variable "subnet_cidr" {
  description = "CIDR block for the public subnet."
  type        = string
  default     = "10.20.1.0/24"
}

variable "cloud_init_user_data" {
  description = "Base64 encoded cloud-init user data. Must not contain application secrets: instance metadata is readable from the instance and is stored in state."
  type        = string
}

variable "freeform_tags" {
  description = "Freeform tags applied to created resources."
  type        = map(string)
  default     = {}
}
