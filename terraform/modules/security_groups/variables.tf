variable "environment" {
  description = "Environment name (dev, live)"
  type        = string
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "marketing-agent"
}

variable "vpc_id" {
  description = "ID of the VPC"
  type        = string
}

variable "ssh_allowed_cidr" {
  description = "CIDR block allowed to SSH (e.g. your IP/32)"
  type        = string
  default     = "0.0.0.0/0"
}

variable "create_rds_sg" {
  description = "Whether to create an RDS security group (live only)"
  type        = bool
  default     = false
}
