# @Study:ST-013 @Study:ST-019
# IAM Module Outputs

output "backend_service_account_role_arn" {
  description = "ARN of the backend service account IAM role"
  value       = var.enable_irsa ? aws_iam_role.backend_service_account[0].arn : null
}

output "backend_service_account_role_name" {
  description = "Name of the backend service account IAM role"
  value       = var.enable_irsa ? aws_iam_role.backend_service_account[0].name : null
}

output "monitoring_service_account_role_arn" {
  description = "ARN of the monitoring service account IAM role"
  value       = var.enable_irsa && var.enable_monitoring ? aws_iam_role.monitoring_service_account[0].arn : null
}

output "ci_cd_role_arn" {
  description = "ARN of the CI/CD IAM role"
  value       = var.enable_ci_cd_role ? aws_iam_role.ci_cd_role[0].arn : null
}

output "ci_cd_role_name" {
  description = "Name of the CI/CD IAM role"
  value       = var.enable_ci_cd_role ? aws_iam_role.ci_cd_role[0].name : null
}

output "oidc_provider_arn" {
  description = "ARN of the OIDC provider"
  value       = var.enable_irsa ? aws_iam_openid_connect_provider.cluster_oidc[0].arn : null
}
