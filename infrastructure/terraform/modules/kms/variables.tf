# @Study:ST-013 @Study:ST-019
# KMS Module Variables

variable "environment" {
  description = "Environment name (e.g., development, staging, production)"
  type        = string
  default     = "development"
}

variable "kms_key_alias" {
  description = "KMS key alias"
  type        = string
  default     = "alias/modamoda-master-key"
}

variable "kms_admin_arns" {
  description = "List of ARNs that can administer the KMS key"
  type        = list(string)
  default     = []
}

variable "kms_user_arns" {
  description = "List of ARNs that can use the KMS key for encryption/decryption"
  type        = list(string)
  default     = []
}

variable "secrets" {
  description = "Map of secrets to create in Secrets Manager"
  type        = map(string)
  default     = {}
  sensitive   = true
}
