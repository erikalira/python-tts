output "instance_id" {
  description = "ID of the bot host instance."
  value       = google_compute_instance.bot.id
}

output "public_ip" {
  description = "Public IP of the bot host. Ephemeral unless use_static_ip is set, in which case it survives instance recreation."
  value       = var.use_static_ip ? google_compute_address.bot[0].address : google_compute_instance.bot.network_interface[0].access_config[0].nat_ip
}

output "public_ip_is_static" {
  description = "Whether the public IP is a reserved static address. Static addresses cost more and keep billing while reserved."
  value       = var.use_static_ip
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
