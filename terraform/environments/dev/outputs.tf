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

output "post_deploy_instructions" {
  description = "Steps to complete after terraform apply"
  value       = <<-EOT

    ============================================
    Dev Environment Deployed Successfully!
    ============================================

    1. SSH into the server:
       ${module.ec2.ssh_command}

    2. Navigate to the project:
       cd marketing-social-agent

    3. Configure environment variables:
       nano .env                  # Set POSTGRES_PASSWORD, REDIS_PASSWORD
       nano backend/.env          # Set API keys, DATABASE_URL, REDIS_URL, SECRET_KEY

    4. Start the application:
       docker compose -f docker-compose.prod.yml up -d --build

    5. Verify:
       docker compose -f docker-compose.prod.yml ps

    6. Open in browser:
       ${module.ec2.public_ip}

    Estimated monthly cost: ~$35 (t3.medium + EIP + storage)
  EOT
}
