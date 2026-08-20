output "instance_id" {
  description = "OCID of the bot host instance."
  value       = oci_core_instance.bot.id
}

output "public_ip" {
  description = "Public IP address of the bot host. Point the DNS record for public_hostname at this address."
  value       = oci_core_instance.bot.public_ip
}

output "ssh_user" {
  description = "Default administrative user for the discovered Ubuntu image."
  value       = "ubuntu"
}

output "image_ocid" {
  description = "Image OCID used for the instance, whether discovered or explicitly provided."
  value       = local.image_ocid
}

output "public_https_enabled" {
  description = "Whether the network security group opens 80/tcp and 443/tcp for the reverse proxy."
  value       = local.https_enabled
}

output "bot_http_publicly_reachable" {
  description = "Whether any rule exposes the bot HTTP port directly. Expected to be false in the default deployment."
  value       = length(var.bot_http_allowed_cidrs) > 0
}

output "network_security_group_id" {
  description = "OCID of the network security group guarding the instance."
  value       = oci_core_network_security_group.bot.id
}
