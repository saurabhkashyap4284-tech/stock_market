# 🚀 Setting Up Oracle Cloud (Always Free)

Follow these steps to create your server and deploy your Stock Market project.

## Step 1: Create a Compute Instance
1. Log in to [Oracle Cloud Console](https://cloud.oracle.com/).
2. Go to **Compute** -> **Instances** -> **Create Instance**.
3. **Name**: `fo-monitor-server`
4. **Placement**: Leave as default.
5. **Image and Shape**:
   - Click **Edit**.
   - **Image**: Ubuntu 22.04 (Standard).
   - **Shape**: Click **Change Shape**.
   - Select **Ampere (ARM-based)**.
   - Choose `VM.Standard.A1.Flex`. 
   - Set **OCPUs: 4** and **Memory: 24 GB** (This is the "Always Free" limit).
   - *If "Out of Capacity", choose `VM.Standard.E2.1.Micro` (AMD-based).*
6. **Networking**: Leave as default (should create a New VCN and Public Subnet).
7. **SSH Keys**: 
   - Select **Generate a key pair for me**.
   - **IMPORTANT**: Click **Save Private Key** and **Save Public Key**. You will need these to log into your server!
8. Click **Create**.

## Step 2: Configure Firewall (Security List)
1. In the Instance details, click on the **Primary VNIC Subnet** link.
2. Click on the **Default Security List**.
3. Click **Add Ingress Rules**.
4. Add the following rule for **HTTP**:
   - **Source CIDR**: `0.0.0.0/0`
   - **IP Protocol**: `TCP`
   - **Destination Port Range**: `80`
   - **Description**: `Allow HTTP traffic`
5. Click **Add Ingress Rules** again (optional but recommended for HTTPS):
   - **Source CIDR**: `0.0.0.0/0`
   - **IP Protocol**: `TCP`
   - **Destination Port Range**: `443`
6. Click **Add Ingress Rules** again for **API/WebSockets** (since we use port 80/443 via Nginx, this is already covered).

## Step 3: Log Into Your Server
Open your terminal (PowerShell or Command Prompt) on your local computer:

```bash
# Replace <private_key_path> with the path to the key you saved
# Replace <public_ip> with the Instance Public IP from Oracle Console
ssh -i <private_key_path> ubuntu@<public_ip>
```

## Step 4: Deploy the Code
Once inside the server, run these commands:

1. **Get the code**:
   ```bash
   git clone <your-github-repo-url>
   cd <repo-name>
   ```

2. **Run the deployment script**:
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

3. **Profit!** 🚀
   Visit your public IP in the browser: `http://<YOUR_PUBLIC_IP>`
