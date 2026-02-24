output "ec2_public_ip" {
  description = "Public IP address of the EC2 instance"
  value       = module.ec2.public_ip
}

output "ssh_command" {
  description = "SSH command to connect to the instance"
  value       = module.ec2.ssh_command
}

output "app_url" {
  description = "URL to access the application"
  value       = "http://${module.ec2.public_ip}"
}

output "rds_endpoint" {
  description = "RDS endpoint (hostname:port)"
  value       = module.rds.endpoint
}

output "database_url" {
  description = "Full PostgreSQL connection string for backend/.env"
  value       = module.rds.database_url
  sensitive   = true
}

output "post_deploy_instructions" {
  description = "Steps to complete after terraform apply"
  value       = <<-EOT

    ============================================
    Live Environment Deployed Successfully!
    ============================================

    1. Get the RDS connection string:
       terraform output -raw database_url

    2. SSH into the server:
       ${module.ec2.ssh_command}

    3. Navigate to the project:
       cd marketing-social-agent

    4. Configure environment variables:
       nano .env                  # Set REDIS_PASSWORD (no POSTGRES_PASSWORD needed — using RDS)
       nano backend/.env          # Set API keys, SECRET_KEY, REDIS_URL
                                  # Set DATABASE_URL to the value from step 1

    5. Start the application:
       docker compose -f docker-compose.live.yml up -d --build

    6. Verify:
       docker compose -f docker-compose.live.yml ps

    7. Open in browser:
       ${module.ec2.public_ip}

    RDS endpoint: ${module.rds.endpoint}
    Estimated monthly cost: ~$84 (t3.large + RDS db.t3.micro + EIP + storage)
  EOT
}
