variable "environment_name" {
  description = "Short environment name."
  type        = string

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment_name)
    error_message = "environment_name must be one of dev, staging, or prod."
  }
}

variable "runtime_baseline" {
  description = "Runtime shape used by this environment."
  type        = string
}

variable "release_source" {
  description = "Artifact or source of truth used for releases into this environment."
  type        = string
}

variable "compute_target" {
  description = "Host, service, or cluster target for the bot runtime."
  type        = string
}

variable "postgres_required" {
  description = "Whether this environment requires durable Postgres."
  type        = bool
}

variable "redis_required" {
  description = "Whether this environment requires Redis queue coordination."
  type        = bool
}

variable "observability_mode" {
  description = "Expected observability level for this environment."
  type        = string
}

variable "kubernetes_mode" {
  description = "Kubernetes expectation for this environment."
  type        = string
}
