output "instance_id" {
  description = "ID of the bot host instance."
  value       = google_compute_instance.bot.id
}

output "public_ip" {
  description = "Static public IP of the bot host. Point the DNS record for public_hostname at this address."
  value       = google_compute_address.bot.address
}

output "ssh_user" {
  description = "Administrative user configured on the instance."
  value       = var.ssh_username
}

output "public_https_enabled" {
  description = "Whether the firewall opens 80/tcp and 443/tcp for the reverse proxy."
  value       = local.https_enabled
}

output "bot_http_publicly_reachable" {
  description = "Whether any rule exposes the bot HTTP port directly. Expected to be false in the default deployment."
  value       = length(var.bot_http_allowed_cidrs) > 0
}

output "network_name" {
  description = "Name of the VPC guarding the instance."
  value       = google_compute_network.bot.name
}
