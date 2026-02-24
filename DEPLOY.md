# Deploy to Production (AWS)

Two deployment methods: **Terraform** (recommended) or **manual** (legacy).

---

## Option A: Deploy with Terraform (Recommended)

Terraform automates all AWS infrastructure provisioning. Two environments available:

- **Dev** (~$35/month): Single EC2 with Postgres in Docker
- **Live** (~$84/month): EC2 + managed RDS Postgres (automated backups)

### Prerequisites

- [Terraform](https://developer.hashicorp.com/terraform/install) >= 1.5
- AWS CLI configured (`aws configure`) with appropriate IAM permissions
- SSH key pair (`~/.ssh/id_rsa.pub`)
- Your API keys (Anthropic, Google)

### Deploy Dev Environment

```bash
cd terraform/environments/dev

# Initialize Terraform
terraform init

# Preview what will be created
terraform plan -var "ssh_public_key=$(cat ~/.ssh/id_rsa.pub)"

# Create infrastructure
terraform apply -var "ssh_public_key=$(cat ~/.ssh/id_rsa.pub)"

# Note the outputs (IP, SSH command, etc.)
terraform output
```

After apply, SSH in and configure:

```bash
# SSH into the instance (use the ssh_command from terraform output)
ssh ubuntu@<EC2_IP>

cd marketing-social-agent
nano .env                  # Set POSTGRES_PASSWORD, REDIS_PASSWORD
nano backend/.env          # Set ANTHROPIC_API_KEY, GOOGLE_API_KEY, SECRET_KEY, DATABASE_URL, REDIS_URL

docker compose -f docker-compose.prod.yml up -d --build
```

### Deploy Live Environment

```bash
cd terraform/environments/live

terraform init

terraform plan \
  -var "ssh_public_key=$(cat ~/.ssh/id_rsa.pub)" \
  -var "db_password=YOUR_STRONG_PASSWORD"

terraform apply \
  -var "ssh_public_key=$(cat ~/.ssh/id_rsa.pub)" \
  -var "db_password=YOUR_STRONG_PASSWORD"

# Get the RDS connection string for backend/.env
terraform output -raw database_url
```

After apply, SSH in and configure:

```bash
ssh ubuntu@<EC2_IP>

cd marketing-social-agent
nano .env                  # Set REDIS_PASSWORD only (no Postgres needed)
nano backend/.env          # Set ANTHROPIC_API_KEY, GOOGLE_API_KEY, SECRET_KEY, REDIS_URL
                           # Set DATABASE_URL to the value from `terraform output -raw database_url`

docker compose -f docker-compose.live.yml up -d --build
```

### Terraform Management

```bash
# Check current state
terraform show

# Update infrastructure after changing .tf files
terraform plan && terraform apply

# Tear down (will prompt for confirmation)
# WARNING: Live env has deletion_protection on RDS — disable in AWS console first
terraform destroy
```

### Terraform File Structure

```
terraform/
  modules/
    vpc/              # VPC, subnets, internet gateway
    security_groups/  # EC2 and RDS security groups
    ec2/              # EC2 instance, EIP, key pair, user_data
    rds/              # RDS PostgreSQL (live only)
  environments/
    dev/              # Dev environment config
    live/             # Live environment config
```

---

## Option B: Manual Deployment (Legacy)

### Prerequisites

- AWS account with EC2 access
- A domain name (optional but recommended for SSL)
- Your API keys ready:
  - Anthropic API key (`sk-ant-...`)
  - Google API key

---

### Step 1: Launch EC2 Instance

1. Go to **EC2 > Launch Instance** in the AWS console
2. Settings:
   - **Name**: `marketing-agent-dev`
   - **AMI**: Ubuntu 24.04 LTS
   - **Instance type**: `t3.medium` (2 vCPU, 4GB RAM) — minimum recommended
   - **Key pair**: Create or select an existing SSH key
   - **Storage**: 30GB gp3
3. **Security Group** — allow these inbound rules:

   | Type  | Port | Source    | Purpose         |
   |-------|------|-----------|-----------------|
   | SSH   | 22   | Your IP   | SSH access      |
   | HTTP  | 80   | 0.0.0.0/0 | Web traffic     |
   | HTTPS | 443  | 0.0.0.0/0 | SSL web traffic |

   **Do NOT open** ports 5432 (Postgres), 6379 (Redis), or 8000 (backend API).

4. Launch the instance and note the **public IP address**

---

### Step 2: Install Docker on the Server

```bash
ssh -i your-key.pem ubuntu@YOUR_SERVER_IP

# Install Docker
curl -fsSL https://get.docker.com | sh

# Add your user to the docker group (avoids needing sudo)
sudo usermod -aG docker $USER

# Log out and back in for group change to take effect
exit
ssh -i your-key.pem ubuntu@YOUR_SERVER_IP

# Verify
docker --version
docker compose version
```

---

### Step 3: Clone the Repository

```bash
git clone YOUR_REPO_URL marketing-social-agent
cd marketing-social-agent
```

---

### Step 4: Configure Environment Variables

#### 4a. Root `.env` (Docker Compose variables)

```bash
cp .env.production.example .env
nano .env
```

Fill in strong passwords:

```
POSTGRES_PASSWORD=your-strong-db-password-here
REDIS_PASSWORD=your-strong-redis-password-here
```

> Generate strong passwords with: `openssl rand -hex 24`

#### 4b. Backend `.env` (API keys and app config)

```bash
cp backend/.env.production.example backend/.env
nano backend/.env
```

Fill in your real values:

```
ANTHROPIC_API_KEY=sk-ant-your-real-key
GOOGLE_API_KEY=your-real-google-key

DATABASE_URL=postgresql://marketing_user:your-strong-db-password-here@postgres:5432/marketing_agents
REDIS_URL=redis://:your-strong-redis-password-here@redis:6379/0

SECRET_KEY=generate-a-random-secret-see-below
ALLOWED_ORIGINS=http://YOUR_SERVER_IP,https://yourdomain.com
```

> Generate a secret key with: `python3 -c "import secrets; print(secrets.token_hex(32))"`

**Important**: The `POSTGRES_PASSWORD` and `REDIS_PASSWORD` values must match between the root `.env` and `backend/.env` (in the DATABASE_URL and REDIS_URL).

---

### Step 5: Update Nginx Config (if using a domain)

If you have a domain pointed at the server, edit `nginx/nginx.conf`:

```bash
nano nginx/nginx.conf
```

Replace `server_name _;` with your domain:

```
server_name yourdomain.com;
```

If you don't have a domain yet, leave it as-is — it will work via the server IP.

---

### Step 6: Build and Start

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

This will:
- Build the backend Docker image (takes a few minutes first time due to Playwright/Chromium)
- Build the frontend as a static production build
- Start all 6 services (postgres, redis, backend, celery, frontend/nginx, certbot)

Check everything is running:

```bash
docker compose -f docker-compose.prod.yml ps
```

All services should show `Up` and `healthy`.

---

### Step 7: Verify It Works

Open your browser and go to:

```
http://YOUR_SERVER_IP
```

You should see the Marketing Agent dashboard. Try creating a campaign to verify the backend and celery worker are functioning.

---

### Step 8: Set Up SSL (Optional but Recommended)

If you have a domain pointed at the server:

#### 8a. Get a certificate

```bash
docker compose -f docker-compose.prod.yml run --rm certbot certonly \
  --webroot \
  --webroot-path /var/www/certbot \
  -d yourdomain.com \
  --email your@email.com \
  --agree-tos \
  --no-eff-email
```

#### 8b. Enable HTTPS in nginx

Edit `nginx/nginx.conf`:

1. Uncomment `return 301 https://$host$request_uri;` in the HTTP server block
2. Uncomment the entire HTTPS server block at the bottom
3. Replace `YOUR_DOMAIN` with your actual domain

#### 8c. Reload nginx

```bash
docker compose -f docker-compose.prod.yml restart frontend
```

#### 8d. Update CORS

In `backend/.env`, update `ALLOWED_ORIGINS` to use https:

```
ALLOWED_ORIGINS=https://yourdomain.com
```

Then restart the backend:

```bash
docker compose -f docker-compose.prod.yml restart backend celery-worker
```

Certbot auto-renews certificates via the certbot container (checks every 12 hours).

---

### Common Operations

#### View logs

```bash
# All services
docker compose -f docker-compose.prod.yml logs -f

# Specific service
docker compose -f docker-compose.prod.yml logs -f backend
docker compose -f docker-compose.prod.yml logs -f celery-worker
```

#### Restart services

```bash
docker compose -f docker-compose.prod.yml restart backend celery-worker
```

#### Pull latest code and redeploy

```bash
git pull
docker compose -f docker-compose.prod.yml up -d --build
```

#### Stop everything

```bash
docker compose -f docker-compose.prod.yml down
```

#### Stop everything AND delete data (database, redis, storage)

```bash
docker compose -f docker-compose.prod.yml down -v
```

> **Warning**: `-v` deletes all volumes including your database. Only use this for a full reset.

---

### Security Checklist

- [ ] `.env` files are **not** committed to git (check with `git status`)
- [ ] Strong passwords set for Postgres and Redis
- [ ] `SECRET_KEY` is a random hex string, not the default
- [ ] Only ports 22, 80, 443 are open in the EC2 security group
- [ ] `DEBUG=false` in backend `.env`
- [ ] `ALLOWED_ORIGINS` set to your actual domain (not `*`)
- [ ] SSH key access only (no password auth)

---

### Troubleshooting

#### Backend won't start

```bash
docker compose -f docker-compose.prod.yml logs backend
```

Common causes:
- Missing or incorrect `ANTHROPIC_API_KEY` in `backend/.env`
- Password mismatch between root `.env` and `backend/.env`

#### Campaigns stuck on "running"

```bash
docker compose -f docker-compose.prod.yml logs celery-worker
```

Check the celery worker is running and connected to Redis.

#### Frontend shows blank page

```bash
docker compose -f docker-compose.prod.yml logs frontend
```

Check that nginx is serving and the API proxy is working. Try hitting `http://YOUR_SERVER_IP/api/health` directly.

#### Can't connect to the site

- Check the EC2 security group allows inbound on port 80
- Check nginx is running: `docker compose -f docker-compose.prod.yml ps frontend`
