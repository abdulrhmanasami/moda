# @Study:ST-013 @Study:ST-019
# KMS Module Outputs

output "kms_key_id" {
  description = "KMS key ID"
  value       = aws_kms_key.modamoda_master_key.key_id
}

output "kms_key_arn" {
  description = "KMS key ARN"
  value       = aws_kms_key.modamoda_master_key.arn
}

output "kms_key_alias" {
  description = "KMS key alias name"
  value       = aws_kms_alias.modamoda_master_key_alias.name
}

output "secrets_arns" {
  description = "Map of secret names to ARNs"
  value       = { for k, v in aws_secretsmanager_secret.modamoda_secrets : k => v.arn }
}

output "secrets_access_policy_arn" {
  description = "ARN of the IAM policy for accessing secrets"
  value       = aws_iam_policy.secrets_access_policy.arn
}

output "secrets_access_policy_name" {
  description = "Name of the IAM policy for accessing secrets"
  value       = aws_iam_policy.secrets_access_policy.name
}
