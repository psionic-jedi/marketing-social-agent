variable "environment" {
  description = "Environment name (dev, live)"
  type        = string
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "marketing-agent"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "create_rds_subnet_group" {
  description = "Whether to create an RDS subnet group (live only)"
  type        = bool
  default     = false
}
