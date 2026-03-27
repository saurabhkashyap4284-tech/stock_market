# ☁️ Setting Up AWS Free Tier (EC2)

Follow these steps to create your server and deploy your Stock Market project for free on Amazon Web Services.

## Step 1: Create an EC2 Instance
1. Log in to [AWS Console](https://console.aws.amazon.com/ec2/).
2. Click **Launch Instance**.
3. **Name**: `fo-monitor-aws`
4. **Application and OS Image (Amazon Machine Image)**:
   - Select **Ubuntu**.
   - Ensure it says **Ubuntu Server 22.04 LTS (HVM), SSD Volume Type** (Free tier eligible).
5. **Instance Type**:
   - Choose `t2.micro` (or `t3.micro` if available in your region) - Ensure it says **Free tier eligible**.
6. **Key Pair (login)**:
   - Click **Create new key pair**.
   - **Name**: `fo-aws-key`
   - **Type**: RSA
   - **Format**: `.pem` (for SSH) or `.ppk` (for PuTTY).
   - **IMPORTANT**: Download and save this file securely.
7. **Network Settings**:
   - Select **Allow SSH traffic from (Anywhere 0.0.0.0/0)**.
   - Select **Allow HTTP traffic from the internet**.
   - Select **Allow HTTPS traffic from the internet**.
8. **Configure Storage**:
   - Set to **30 GiB** (This is the max for AWS Free Tier - always use the full 30GB!).
9. Click **Launch Instance**.

## Step 2: Set Up Floating IP (Elastic IP) - Optional but Recommended
1. In EC2 Dashboard, go to **Network & Security** -> **Elastic IPs**.
2. Click **Allocate Elastic IP address** -> **Allocate**.
3. Select the IP -> **Actions** -> **Associate Elastic IP address**.
4. Choose your new instance and click **Associate**. (This makes your URL stay the same if you restart the server).

## Step 3: Log Into Your Server
Open your terminal (PowerShell or Command Prompt) on your local computer:

```bash
# Replace <key_path> with the path to your .pem file
# Replace <public_ip> with the Public IP of your EC2 instance
ssh -i <key_path> ubuntu@<public_ip>
```

## Step 4: Deploy the Code (The "Single Command" Magic)
Once inside the server, run these commands:

1. **Clone the project**:
   ```bash
   git clone <your-github-repo-url>
   cd <repo-name>
   ```

2. **Run the AWS specific script**:
   ```bash
   chmod +x deploy_aws.sh
   ./deploy_aws.sh
   ```

3. **Profit!** 🚀
   Visit your public IP in the browser: `http://<YOUR_AWS_IP>`
