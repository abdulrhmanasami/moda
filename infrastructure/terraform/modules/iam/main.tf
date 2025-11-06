# @Study:ST-013 @Study:ST-019
# IAM Roles and Policies for MODA

# OIDC Provider for IRSA
data "tls_certificate" "cluster_oidc" {
  count = var.enable_irsa ? 1 : 0
  url   = var.cluster_oidc_issuer_url
}

resource "aws_iam_openid_connect_provider" "cluster_oidc" {
  count = var.enable_irsa ? 1 : 0
  url   = var.cluster_oidc_issuer_url

  client_id_list = [
    "sts.amazonaws.com",
  ]

  thumbprint_list = [data.tls_certificate.cluster_oidc[0].certificates[0].sha1_fingerprint]

  tags = {
    Name = "modamoda-oidc-provider"
  }
}

# IAM Role for Backend Service Account (IRSA)
resource "aws_iam_role" "backend_service_account" {
  count = var.enable_irsa ? 1 : 0
  name  = "modamoda-backend-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = aws_iam_openid_connect_provider.cluster_oidc[0].arn
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            "${replace(var.cluster_oidc_issuer_url, "https://", "")}:sub" = "system:serviceaccount:${var.backend_namespace}:${var.backend_service_account_name}"
          }
        }
      }
    ]
  })

  tags = {
    Name        = "modamoda-backend-service-account"
    Environment = var.environment
    Purpose     = "IRSA"
  }
}

# Attach policies to backend service account role
resource "aws_iam_role_policy_attachment" "backend_secrets_access" {
  count      = var.enable_irsa ? 1 : 0
  role       = aws_iam_role.backend_service_account[0].name
  policy_arn = var.secrets_access_policy_arn
}

resource "aws_iam_role_policy_attachment" "backend_kms_access" {
  count      = var.enable_irsa ? 1 : 0
  role       = aws_iam_role.backend_service_account[0].name
  policy_arn = "arn:aws:iam::aws:policy/AWSKeyManagementServicePowerUser"
}

# Additional policy for backend (S3, CloudWatch, etc.)
resource "aws_iam_role_policy" "backend_additional_permissions" {
  count = var.enable_irsa ? 1 : 0
  name  = "ModamodaBackendAdditionalPermissions-${var.environment}"
  role  = aws_iam_role.backend_service_account[0].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::${var.storage_bucket_name}",
          "arn:aws:s3:::${var.storage_bucket_name}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogStreams"
        ]
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Effect = "Allow"
        Action = [
          "cloudwatch:PutMetricData",
          "cloudwatch:GetMetricData",
          "cloudwatch:ListMetrics"
        ]
        Resource = "*"
      }
    ]
  })
}

# IAM Role for Monitoring Service Account (Prometheus)
resource "aws_iam_role" "monitoring_service_account" {
  count = var.enable_irsa && var.enable_monitoring ? 1 : 0
  name  = "modamoda-monitoring-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = aws_iam_openid_connect_provider.cluster_oidc[0].arn
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            "${replace(var.cluster_oidc_issuer_url, "https://", "")}:sub" = "system:serviceaccount:${var.monitoring_namespace}:${var.monitoring_service_account_name}"
          }
        }
      }
    ]
  })

  tags = {
    Name        = "modamoda-monitoring-service-account"
    Environment = var.environment
    Purpose     = "IRSA"
  }
}

# Attach CloudWatch permissions to monitoring role
resource "aws_iam_role_policy" "monitoring_permissions" {
  count = var.enable_irsa && var.enable_monitoring ? 1 : 0
  name  = "ModamodaMonitoringPermissions-${var.environment}"
  role  = aws_iam_role.monitoring_service_account[0].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "cloudwatch:PutMetricData",
          "cloudwatch:GetMetricData",
          "cloudwatch:ListMetrics",
          "cloudwatch:GetMetricStatistics",
          "cloudwatch:ListMetrics"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogStreams",
          "logs:DescribeLogGroups"
        ]
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

# IAM Role for CI/CD Pipeline
resource "aws_iam_role" "ci_cd_role" {
  count = var.enable_ci_cd_role ? 1 : 0
  name  = "modamoda-cicd-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          AWS = var.ci_cd_principal_arns
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = {
    Name        = "modamoda-cicd-role"
    Environment = var.environment
    Purpose     = "CI/CD"
  }
}

# Attach comprehensive permissions to CI/CD role
resource "aws_iam_role_policy" "ci_cd_permissions" {
  count = var.enable_ci_cd_role ? 1 : 0
  name  = "ModamodaCiCdPermissions-${var.environment}"
  role  = aws_iam_role.ci_cd_role[0].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret",
          "secretsmanager:CreateSecret",
          "secretsmanager:UpdateSecret",
          "secretsmanager:DeleteSecret"
        ]
        Resource = "arn:aws:secretsmanager:${var.aws_region}:*:secret:modamoda/${var.environment}/*"
      },
      {
        Effect = "Allow"
        Action = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*",
          "kms:CreateGrant",
          "kms:DescribeKey",
          "kms:RetireGrant"
        ]
        Resource = var.kms_key_arn
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket",
          "s3:GetBucketLocation"
        ]
        Resource = [
          "arn:aws:s3:::${var.storage_bucket_name}",
          "arn:aws:s3:::${var.storage_bucket_name}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetRepositoryPolicy",
          "ecr:ListImages",
          "ecr:DescribeRepositories",
          "ecr:GetAuthorizationToken"
        ]
        Resource = "*"
      }
    ]
  })
}
