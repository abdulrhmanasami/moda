# @Study:ST-013 @Study:ST-019
# IAM Module Variables

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "development"
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "enable_irsa" {
  description = "Enable IAM Roles for Service Accounts (IRSA)"
  type        = bool
  default     = true
}

variable "cluster_oidc_issuer_url" {
  description = "EKS cluster OIDC issuer URL"
  type        = string
  default     = ""
}

variable "backend_namespace" {
  description = "Namespace for backend service account"
  type        = string
  default     = "default"
}

variable "backend_service_account_name" {
  description = "Name of the backend service account"
  type        = string
  default     = "modamoda-backend-sa"
}

variable "monitoring_namespace" {
  description = "Namespace for monitoring service account"
  type        = string
  default     = "monitoring"
}

variable "monitoring_service_account_name" {
  description = "Name of the monitoring service account"
  type        = string
  default     = "prometheus-sa"
}

variable "enable_monitoring" {
  description = "Enable monitoring IAM role"
  type        = bool
  default     = true
}

variable "enable_ci_cd_role" {
  description = "Enable CI/CD IAM role"
  type        = bool
  default     = false
}

variable "ci_cd_principal_arns" {
  description = "Principal ARNs allowed to assume CI/CD role"
  type        = list(string)
  default     = []
}

variable "secrets_access_policy_arn" {
  description = "ARN of the secrets access policy"
  type        = string
  default     = ""
}

variable "kms_key_arn" {
  description = "ARN of the KMS key"
  type        = string
  default     = ""
}

variable "storage_bucket_name" {
  description = "Name of the S3 storage bucket"
  type        = string
  default     = "modamoda-storage"
}
