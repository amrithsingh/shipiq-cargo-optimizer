# Deployment Guide

## 1. Run Locally (without Docker)

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy env file
cp .env.example .env

# Start the server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API available at `http://localhost:8000`
Swagger docs at `http://localhost:8000/docs`

## 2. Run with Docker / Docker Compose

```bash
# Build and run
docker compose up --build

# Or without compose:
docker build -t shipiq-cargo .
docker run -p 8000:8000 shipiq-cargo
```

## 3. Deploy to AWS EC2

### Prerequisites
- An EC2 instance (Ubuntu 22.04 recommended, t2.micro works for testing)
- Docker installed on the instance
- Security group with inbound rule allowing TCP port 8000

### Steps

```bash
# SSH into your EC2 instance
ssh -i your-key.pem ubuntu@<EC2_PUBLIC_IP>

# Install Docker (if not already installed)
sudo apt update && sudo apt install -y docker.io docker-compose-plugin
sudo usermod -aG docker $USER
newgrp docker

# Clone your repo
git clone https://github.com/<your-username>/shipiq-cargo.git
cd shipiq-cargo

# Build and run
docker compose up -d --build

# Verify
curl http://localhost:8000/
```

The API is now accessible at `http://<EC2_PUBLIC_IP>:8000`

## 4. Deploy to Railway

[Railway](https://railway.app) auto-detects the Dockerfile.

1. Push code to GitHub
2. Go to [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub**
3. Select the repository
4. Railway detects the Dockerfile and deploys automatically
5. Go to **Settings** → **Networking** → **Generate Domain** to get a public URL

Environment variables can be set in the Railway dashboard under **Variables**.

## 5. Deploy to Render

[Render](https://render.com) also supports Docker-based deployments.

1. Push code to GitHub
2. Go to [render.com](https://render.com) → **New** → **Web Service**
3. Connect your GitHub repo
4. Configure:
   - **Environment**: Docker
   - **Instance Type**: Free (for testing)
5. Click **Create Web Service**

Render provides a `.onrender.com` URL automatically.
