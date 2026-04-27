output "environment_contract" {
  description = "Normalized infrastructure contract for the production environment."
  value       = module.environment_contract.summary
}
