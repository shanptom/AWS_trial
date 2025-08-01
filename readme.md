# AWS - Hand on experiment-MVP  metabarcoding database

This is a project was created to have hands-on experience with AWS services like S3, EC2, and IAM. It provides a web application for browsing and uploading metabarcoding datasets.
This is a Minimum Viable Product (MVP) that uses S3 for data storage and EC2 for hosting a Streamlit application.   

## 🏗️ Architecture

```
User Request → EC2 (Streamlit App) → S3 (Data Storage)
                    ↓
              IAM (Permissions)
```

## 🛠️ AWS Setup Guide

### Step 1: Create AWS Account

1. Go to [aws.amazon.com](https://aws.amazon.com)
2. Click "Create an AWS Account"
3. Follow the registration process (requires credit card for verification)
4. Complete identity verification

### Step 2: Set Up IAM (Identity and Access Management)

1. **Create IAM User**
   - Go to IAM Console → Users → Add User
   - User name: `microbiome-atlas-user`
   - Access type: ✅ Programmatic access
   - Click Next

2. **Set Permissions**
   - Attach existing policies directly
   - Select: `AmazonS3FullAccess` and `AmazonEC2FullAccess`
   - Click Next → Create User

3. **Save Credentials**
   - Download the CSV file with Access Key ID and Secret Access Key
   - ⚠️ **Important**: Store these securely - you can't retrieve the secret key later

### Step 3: Create S3 Bucket

1. **Go to S3 Console**
   - Navigate to S3 service
   - Click "Create bucket"

2. **Configure Bucket**
   - Bucket name: `microbiome-atlas-data` (must be globally unique)
   - Region: Choose your preferred region (e.g., `us-east-2`)
   - Keep default settings for now
   - Click "Create bucket"

3. **Set Bucket Permissions** (Optional for private data)
   - Go to bucket → Permissions → Bucket Policy
   - Add policy to restrict access if needed

### Step 4: Launch EC2 Instance

1. **Go to EC2 Console**
   - Navigate to EC2 service
   - Click "Launch Instance"

2. **Choose AMI**
   - Select "Amazon Linux 2 AMI" (Free Tier eligible)

3. **Choose Instance Type**
   - Select `t2.micro` (Free Tier eligible)
   - Click "Next: Configure Instance Details"

4. **Configure Instance**
   - Keep default settings
   - Click "Next" until you reach "Configure Security Group"

5. **Configure Security Group**
   - Create new security group: `microbiome-atlas-sg`
   - Add rules:
     - SSH (port 22): Your IP address
     - Custom TCP (port 8501): 0.0.0.0/0 (for Streamlit)
     - HTTP (port 80): 0.0.0.0/0 (optional)
     - Streamlit (port 8501): 0.0.0.0/0 (optional)
   

6. **Review and Launch**
   - Create new key pair: `microbiome-atlas-key`
   - Download the `.pem` file
   - Launch instance

### Step 5: Connect to EC2 Instance

1. **Set Key Permissions** (Linux/Mac)
   ```bash
   chmod 400 microbiome-atlas-key.pem
   ```

2. **Connect via SSH**
   ```bash
   ssh -i microbiome-atlas-key.pem ec2-user@YOUR_EC2_PUBLIC_IP
   ```

## 💻 Application Deployment

### Step 1: Install Dependencies on EC2

```bash
# Update system
sudo yum update -y

# Activate Python 3
python3 -m venv asvenv
source asvenv/bin/activate

# Install git
sudo yum install git -y
```

### Step 2: Clone and Setup Application

```bash
# Clone repository
clone repo from git

# Install Python packages
pip3 install streamlit pandas boto3
```
# Create secrets directory
```bash
mkdir -p .streamlit
cd .streamlit

```
### Step 3: Configure Streamlit Secrets

Create `.streamlit/secrets.toml`:

```toml
[aws] 
access_key = "YOUR_ACCESS_KEY_ID" # Replace with your access key
secret_key = "YOUR_SECRET_ACCESS_KEY" # Replace with your secret key
region = "us-east-1" # Replace with your region
bucket = "bucket-name" # Replace with your bucket name

```

### Step 4: Run the Application

```bash
# Run Streamlit app
streamlit run Home.py
```

### Step 5: Access Your Application

Open your browser and go to:
```
http://YOUR_EC2_PUBLIC_IP:8501
```

## 🔧 Project Structure

```
microbiome-atlas/
├── Home.py              # Main dashboard page
├── pages/
│   └── Upload.py        # Dataset upload page
├── .streamlit/
│   └── secrets.toml     # AWS credentials (not in repo)
└── README.md           # This file
```

## 📦 Dependencies

```txt
streamlit==1.28.0
pandas==2.1.0
boto3==1.28.0
```

## 🔒 Security Best Practices

1. **IAM Permissions**: Use least privilege principle
2. **Security Groups**: Restrict access to necessary ports only
3. **Secrets Management**: Never commit AWS credentials to version control
4. **S3 Bucket**: Consider enabling encryption and versioning
5. **EC2 Updates**: Regularly update your instance

## 💰 Cost Optimization

- **Free Tier**: This setup uses AWS Free Tier eligible services
- **Auto-scaling**: Consider using Auto Scaling Groups for production
- **S3 Storage Classes**: Use appropriate storage classes for data
- **EC2 Scheduling**: Stop instances when not in use

```bash
# Check Streamlit logs
streamlit run Home.py --server.port 8501 --server.address 0.0.0.0 --logger.level debug

# Check system logs
sudo tail -f /var/log/messages
```
Abandoned further development of this project is due to the requirement of paid AWS services for production use, which is not feasible for a personal project.
