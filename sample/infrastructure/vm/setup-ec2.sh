#!/usr/bin/env bash
# ==============================================================================
# setup-ec2.sh
# One-time bootstrap script for Ubuntu 22.04/24.04 LTS on AWS EC2
# Sets up Docker, Docker Compose, Nginx Reverse Proxy, and UFW Firewall.
# ==============================================================================
set -euo pipefail

echo "=========================================================="
echo " Starting AWS EC2 Bootstrap for FastAPI Microservices..."
echo "=========================================================="

# 1. Update OS package repositories
echo " Updating system packages..."
sudo apt-get update -y
sudo apt-get upgrade -y
sudo apt-get install -y ca-certificates curl gnupg lsb-release ufw nginx

# 2. Install Official Docker Engine
echo " Installing Docker Engine & Docker Compose plugin..."
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update -y
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# 3. Add ubuntu user to docker group
echo " Adding user to docker group..."
sudo usermod -aG docker "$USER"

# 4. Enable and start Docker & Nginx services
sudo systemctl enable --now docker
sudo systemctl enable --now nginx

# 5. Create deployment directories
echo " Creating application directory at /opt/fastapi..."
sudo mkdir -p /opt/fastapi/logs
sudo chown -R "$USER":"$USER" /opt/fastapi

# 6. Configure UFW Firewall (SSH, HTTP, HTTPS)
echo " Configuring Firewall (UFW)..."
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

echo "=========================================================="
echo " EC2 Bootstrap Complete!"
echo "Docker Version: $(docker --version)"
echo "Note: Re-login or run 'newgrp docker' to use docker without sudo."
echo "=========================================================="
