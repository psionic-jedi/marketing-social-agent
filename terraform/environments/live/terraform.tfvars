aws_region       = "ap-southeast-2"
environment      = "live"
project_name     = "marketing-agent"
instance_type    = "t3.large"
root_volume_size = 50

# RDS
db_instance_class        = "db.t3.micro"
db_allocated_storage     = 20
db_max_allocated_storage = 50

# Restrict SSH to your IP for security (e.g. "203.0.113.1/32")
# ssh_allowed_cidr = "0.0.0.0/0"

# Set your repo URL to auto-clone on instance creation
# repo_url = "https://github.com/your-user/marketing-social-agent.git"

# IMPORTANT: db_password is NOT set here — pass via CLI:
#   terraform apply -var "ssh_public_key=$(cat ~/.ssh/id_rsa.pub)" -var "db_password=YOUR_STRONG_PASSWORD"
