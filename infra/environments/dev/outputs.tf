output "environment_contract" {
  description = "Normalized infrastructure contract for the dev environment."
  value       = module.environment_contract.summary
}
