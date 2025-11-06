terraform {

  required_version = ">= 1.6.0"

  backend "s3" {

    bucket         = "modamoda-tfstate"

    key            = "envs/prod/terraform.tfstate"

    region         = "eu-central-1"

    dynamodb_table = "modamoda-tf-locks"

    encrypt        = true

  }

  required_providers {

    aws = {

      source  = "hashicorp/aws"

      version = "~> 5.0"

    }

  }

}

provider "aws" {

  region = "eu-central-1"

}
