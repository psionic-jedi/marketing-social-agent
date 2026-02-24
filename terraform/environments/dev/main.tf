terraform {
  required_version = ">= 1.5"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Environment = var.environment
      Project     = var.project_name
      ManagedBy   = "terraform"
    }
  }
}

# --- VPC ---

module "vpc" {
  source = "../../modules/vpc"

  environment             = var.environment
  project_name            = var.project_name
  create_rds_subnet_group = false
}

# --- Security Groups ---

module "security_groups" {
  source = "../../modules/security_groups"

  environment      = var.environment
  project_name     = var.project_name
  vpc_id           = module.vpc.vpc_id
  ssh_allowed_cidr = var.ssh_allowed_cidr
  create_rds_sg    = false
}

# --- EC2 Instance ---

module "ec2" {
  source = "../../modules/ec2"

  environment       = var.environment
  project_name      = var.project_name
  instance_type     = var.instance_type
  root_volume_size  = var.root_volume_size
  subnet_id         = module.vpc.public_subnet_ids[0]
  security_group_id = module.security_groups.ec2_security_group_id
  ssh_public_key    = var.ssh_public_key
  repo_url          = var.repo_url
  compose_file      = "docker-compose.prod.yml"
}
