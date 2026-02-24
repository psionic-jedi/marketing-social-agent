variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "ap-southeast-2"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "live"
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "marketing-agent"
}

variable "ssh_public_key" {
  description = "SSH public key for EC2 access"
  type        = string
}

variable "ssh_allowed_cidr" {
  description = "CIDR block allowed to SSH (e.g. your IP/32)"
  type        = string
  default     = "0.0.0.0/0"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.large"
}

variable "root_volume_size" {
  description = "Root EBS volume size in GB"
  type        = number
  default     = 50
}

variable "repo_url" {
  description = "Git repository URL to clone on the instance"
  type        = string
  default     = ""
}

# RDS variables

variable "db_password" {
  description = "RDS master password (pass via -var at apply time, never in tfvars)"
  type        = string
  sensitive   = true
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "db_allocated_storage" {
  description = "RDS initial storage in GB"
  type        = number
  default     = 20
}

variable "db_max_allocated_storage" {
  description = "RDS maximum storage for autoscaling in GB"
  type        = number
  default     = 50
}
