#!/usr/bin/env python3
"""
Deployment script for fraud detection system.
"""
import subprocess
import sys
import argparse
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ {description} failed!")
        print(f"Error: {result.stderr}")
        return False
    else:
        print(f"✅ {description} completed!")
        return True

def deploy_docker(environment="dev"):
    """Deploy using Docker Compose."""
    deployment_dir = Path(__file__).parent.parent
    
    if environment == "dev":
        compose_file = deployment_dir / "docker" / "docker-compose.yml"
    else:
        compose_file = deployment_dir / "docker" / "docker-compose-kafka.yml"
    
    cmd = f"docker-compose -f {compose_file} up -d"
    return run_command(cmd, f"Docker deployment ({environment})")

def deploy_kubernetes():
    """Deploy to Kubernetes."""
    deployment_dir = Path(__file__).parent.parent / "kubernetes"
    
    # Apply all Kubernetes manifests
    for manifest_dir in deployment_dir.iterdir():
        if manifest_dir.is_dir():
            cmd = f"kubectl apply -f {manifest_dir}/"
            if not run_command(cmd, f"Kubernetes deployment ({manifest_dir.name})"):
                return False
    return True

def main():
    parser = argparse.ArgumentParser(description="Deploy fraud detection system")
    parser.add_argument("--platform", choices=["docker", "kubernetes"], default="docker")
    parser.add_argument("--environment", choices=["dev", "prod"], default="dev")
    
    args = parser.parse_args()
    
    print(f"🚀 Deploying to {args.platform} ({args.environment})...")
    
    if args.platform == "docker":
        success = deploy_docker(args.environment)
    else:
        success = deploy_kubernetes()
    
    if success:
        print("🎉 Deployment completed successfully!")
    else:
        print("❌ Deployment failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()