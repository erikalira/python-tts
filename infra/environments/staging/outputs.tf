output "environment_contract" {
  description = "Normalized infrastructure contract for the staging environment."
  value       = module.environment_contract.summary
}
