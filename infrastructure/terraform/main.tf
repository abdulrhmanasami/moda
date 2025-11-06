# @Study:ST-012 @Study:ST-019
# Modamoda Infrastructure as Code - Main Configuration

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.0"
    }
  }

  backend "s3" {
    bucket         = "modamoda-terraform-state"
    key            = "infrastructure/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "modamoda-terraform-locks"
  }
}

# AWS Provider Configuration
provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "Modamoda"
      Environment = var.environment
      ManagedBy   = "Terraform"
      Study       = "ST-012"
    }
  }
}

# Data sources
data "aws_caller_identity" "current" {}
data "aws_availability_zones" "available" {}

# VPC Module
module "vpc" {
  source = "./modules/vpc"

  environment         = var.environment
  vpc_cidr           = var.vpc_cidr
  availability_zones = data.aws_availability_zones.available.names

  tags = {
    Name = "modamoda-${var.environment}"
  }
}

# Security Groups
module "security_groups" {
  source = "./modules/security_groups"

  environment = var.environment
  vpc_id      = module.vpc.vpc_id

  depends_on = [module.vpc]
}

# RDS Database
module "rds" {
  source = "./modules/rds"

  environment          = var.environment
  vpc_id              = module.vpc.vpc_id
  subnet_ids          = module.vpc.private_subnet_ids
  security_group_ids  = [module.security_groups.rds_sg_id]

  db_name             = var.db_name
  db_username         = var.db_username
  db_password         = var.db_password
  db_instance_class   = var.db_instance_class

  depends_on = [module.vpc, module.security_groups]
}

# ElastiCache Redis
module "redis" {
  source = "./modules/redis"

  environment         = var.environment
  vpc_id             = module.vpc.vpc_id
  subnet_ids         = module.vpc.private_subnet_ids
  security_group_ids = [module.security_groups.redis_sg_id]

  node_type          = var.redis_node_type
  num_cache_nodes    = var.redis_num_cache_nodes

  depends_on = [module.vpc, module.security_groups]
}

# S3 Storage
module "s3" {
  source = "./modules/s3"

  environment = var.environment
  bucket_name = var.s3_bucket_name

  enable_versioning = true
  enable_encryption = true
}

# CloudFront CDN
module "cloudfront" {
  source = "./modules/cloudfront"

  environment     = var.environment
  s3_bucket_id    = module.s3.bucket_id
  s3_bucket_arn   = module.s3.bucket_arn
  s3_domain_name  = module.s3.bucket_domain_name

  depends_on = [module.s3]
}

# ECS Cluster
module "ecs" {
  source = "./modules/ecs"

  environment         = var.environment
  vpc_id             = module.vpc.vpc_id
  subnet_ids         = module.vpc.private_subnet_ids
  security_group_ids = [module.security_groups.ecs_sg_id]

  app_image          = var.app_image
  app_count          = var.app_count
  app_port           = var.app_port
  fargate_cpu        = var.fargate_cpu
  fargate_memory     = var.fargate_memory

  depends_on = [module.vpc, module.security_groups, module.rds, module.redis]
}

# API Gateway
module "api_gateway" {
  source = "./modules/api_gateway"

  environment = var.environment
  app_alb_arn = module.ecs.alb_arn

  depends_on = [module.ecs]
}

# WAF
module "waf" {
  source = "./modules/waf"

  environment = var.environment

  # Associate with API Gateway or CloudFront
  resource_arn = module.api_gateway.api_arn
}

# Monitoring and Logging
module "monitoring" {
  source = "./modules/monitoring"

  environment = var.environment
  region      = var.aws_region

  ecs_cluster_name = module.ecs.cluster_name
  rds_instance_id  = module.rds.instance_id
  redis_cluster_id = module.redis.cluster_id

  depends_on = [module.ecs, module.rds, module.redis]
}

# Outputs
output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}

output "rds_endpoint" {
  description = "RDS endpoint"
  value       = module.rds.endpoint
  sensitive   = true
}

output "redis_endpoint" {
  description = "Redis endpoint"
  value       = module.redis.endpoint
  sensitive   = true
}

output "s3_bucket_name" {
  description = "S3 bucket name"
  value       = module.s3.bucket_name
}

output "cloudfront_domain_name" {
  description = "CloudFront domain name"
  value       = module.cloudfront.domain_name
}

output "api_gateway_url" {
  description = "API Gateway URL"
  value       = module.api_gateway.api_url
}

output "ecs_cluster_name" {
  description = "ECS cluster name"
  value       = module.ecs.cluster_name
}
