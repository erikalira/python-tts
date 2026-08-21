output "environment_contract" {
  description = "Normalized infrastructure contract for the GCP e2-micro environment."
  value       = module.environment_contract.summary
}

output "instance_public_ip" {
  description = "Public IP of the bot host. Create the DNS record for public_hostname pointing here."
  value       = module.bot_host.public_ip
}

output "public_ip_is_static" {
  description = "Whether the public IP is a reserved static address. Ephemeral by default because GCP bills static addresses at a higher rate."
  value       = module.bot_host.public_ip_is_static
}

output "ssh_command" {
  description = "Ready to use SSH command for the bot host."
  value       = "ssh ${module.bot_host.ssh_user}@${module.bot_host.public_ip}"
}

output "app_dir" {
  description = "Application directory prepared on the instance by cloud-init."
  value       = var.app_dir
}

output "public_https_enabled" {
  description = "Whether public HTTPS ingress is enabled for the reverse proxy."
  value       = module.bot_host.public_https_enabled
}

output "bot_http_publicly_reachable" {
  description = "Whether the bot HTTP port is directly reachable from any allowlisted CIDR. Expected to be false."
  value       = module.bot_host.bot_http_publicly_reachable
}
