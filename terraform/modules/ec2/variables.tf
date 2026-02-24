variable "environment" {
  description = "Environment name (dev, live)"
  type        = string
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "marketing-agent"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.medium"
}

variable "root_volume_size" {
  description = "Root EBS volume size in GB"
  type        = number
  default     = 30
}

variable "subnet_id" {
  description = "Subnet ID to launch the instance in"
  type        = string
}

variable "security_group_id" {
  description = "Security group ID for the instance"
  type        = string
}

variable "ssh_public_key" {
  description = "SSH public key for EC2 access"
  type        = string
}

variable "repo_url" {
  description = "Git repository URL to clone"
  type        = string
  default     = ""
}

variable "compose_file" {
  description = "Docker compose file to use (docker-compose.prod.yml or docker-compose.live.yml)"
  type        = string
  default     = "docker-compose.prod.yml"
}
