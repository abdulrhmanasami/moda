# @Study:ST-013 @Study:ST-019
# AWS KMS and Secrets Manager Terraform Module

# KMS Key for encrypting secrets
resource "aws_kms_key" "modamoda_master_key" {
  description             = "Master encryption key for Modamoda application secrets"
  deletion_window_in_days = 30
  key_usage              = "ENCRYPT_DECRYPT"
  key_spec               = "SYMMETRIC_DEFAULT"
  origin                 = "AWS_KMS"

  tags = {
    Name        = "modamoda-master-key"
    Project     = "Modamoda"
    Environment = var.environment
    Purpose     = "SecretEncryption"
  }

  # Enable automatic key rotation
  enable_key_rotation = true

  # Key policy for secure access
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "Enable IAM User Permissions"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Action   = "kms:*"
        Resource = "*"
      },
      {
        Sid    = "Allow access for Key Administrators"
        Effect = "Allow"
        Principal = {
          AWS = var.kms_admin_arns
        }
        Action = [
          "kms:Create*",
          "kms:Describe*",
          "kms:Enable*",
          "kms:List*",
          "kms:Put*",
          "kms:Update*",
          "kms:Revoke*",
          "kms:Disable*",
          "kms:Get*",
          "kms:Delete*",
          "kms:TagResource",
          "kms:UntagResource",
          "kms:ScheduleKeyDeletion",
          "kms:CancelKeyDeletion"
        ]
        Resource = "*"
      },
      {
        Sid    = "Allow use of the key"
        Effect = "Allow"
        Principal = {
          AWS = var.kms_user_arns
        }
        Action = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*",
          "kms:DescribeKey"
        ]
        Resource = "*"
      },
      {
        Sid    = "Allow Secrets Manager to use the key"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/aws-service-role/secretsmanager.amazonaws.com/AWSServiceRoleForSecretsManager"
        }
        Action = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*",
          "kms:CreateGrant",
          "kms:DescribeKey"
        ]
        Resource = "*"
      }
    ]
  })
}

# KMS Key Alias
resource "aws_kms_alias" "modamoda_master_key_alias" {
  name          = var.kms_key_alias
  target_key_id = aws_kms_key.modamoda_master_key.key_id
}

# Secrets Manager secrets
resource "aws_secretsmanager_secret" "modamoda_secrets" {
  for_each = var.secrets

  name                    = "modamoda/${var.environment}/${each.key}"
  description             = "Modamoda ${var.environment} secret: ${each.key}"
  kms_key_id              = aws_kms_key.modamoda_master_key.key_id
  recovery_window_in_days = 30

  tags = {
    Name        = "modamoda-${var.environment}-${each.key}"
    Project     = "Modamoda"
    Environment = var.environment
    Purpose     = "ApplicationSecret"
  }
}

# Secret versions
resource "aws_secretsmanager_secret_version" "modamoda_secret_versions" {
  for_each = var.secrets

  secret_id = aws_secretsmanager_secret.modamoda_secrets[each.key].id
  secret_string = jsonencode({
    value       = each.value
    environment = var.environment
    created     = timestamp()
  })
}

# IAM Policy for accessing secrets
resource "aws_iam_policy" "secrets_access_policy" {
  name        = "ModamodaSecretsAccess-${var.environment}"
  description = "Policy for accessing Modamoda secrets in ${var.environment}"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        Resource = values(aws_secretsmanager_secret.modamoda_secrets)[*].arn
      },
      {
        Effect = "Allow"
        Action = [
          "kms:Decrypt",
          "kms:DescribeKey"
        ]
        Resource = aws_kms_key.modamoda_master_key.arn
      }
    ]
  })
}

# Data source for current AWS account
data "aws_caller_identity" "current" {}
