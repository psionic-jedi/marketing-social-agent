#!/bin/bash
set -euo pipefail

# Log all output
exec > >(tee /var/log/user-data.log) 2>&1
echo "=== User data script starting at $(date) ==="

# Update system
apt-get update -y
apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sh

# Add ubuntu user to docker group
usermod -aG docker ubuntu

# Enable Docker to start on boot
systemctl enable docker
systemctl start docker

# Install useful tools
apt-get install -y git make jq

# Clone the repository (if URL provided)
%{ if repo_url != "" ~}
cd /home/ubuntu
git clone ${repo_url} marketing-social-agent
chown -R ubuntu:ubuntu marketing-social-agent

# Create placeholder .env files
cd marketing-social-agent
cp .env.production.example .env 2>/dev/null || true
cp backend/.env.production.example backend/.env 2>/dev/null || true
%{ endif ~}

echo "=== User data script completed at $(date) ==="
echo "=== Next steps: SSH in, fill .env files, then run: ==="
echo "===   cd marketing-social-agent ==="
echo "===   docker compose -f ${compose_file} up -d --build ==="
