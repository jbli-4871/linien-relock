#!/bin/bash

# Deployment script for pushing modified linien_server code
# to a Red Pitaya and rebooting the device.

set -e  # Stop on any error

echo "------------------------------------------------------------"
echo "    LINIEN SERVER DEPLOYMENT STARTED"
echo "------------------------------------------------------------"
echo ""

### ------------------------------
### CONFIGURATION (EDIT THESE)
### ------------------------------
RP_IP="rp-XXXXXX.local"        # Red Pitaya IP address
LOCAL_DIR="./linien/server"    # Local modified server directory
RP_TARGET_DIR="/usr/local/lib/python3.5/dist-packages/linien/server"   # Remote install path
### ------------------------------

# 1. Verify that the local folder exists
if [ ! -d "$LOCAL_DIR" ]; then
    echo "ERROR: Local directory '$LOCAL_DIR' does not exist."
    exit 1
fi

echo "Local directory: $LOCAL_DIR"
echo "Remote directory: $RP_TARGET_DIR"
echo ""

# 2. Test SSH connection (passwordless)
echo "Testing SSH connectivity to Red Pitaya ($RP_IP)..."

if ssh -o BatchMode=yes root@"$RP_IP" "echo test" >/dev/null 2>&1 ; then
    echo "SSH connection OK (passwordless)"
else
    echo "ERROR: Cannot connect via SSH without password."
    echo "You must set up SSH keys first:"
    echo ""
    echo "   ssh-copy-id root@$RP_IP"
    echo ""
    exit 1
fi

echo ""

# 3. Copy modified files to the Red Pitaya
echo "Copying modified linien_server files to Red Pitaya..."
scp -r "$LOCAL_DIR"/* root@"$RP_IP":"$RP_TARGET_DIR"/

echo "Files copied successfully."
echo ""

# 4. Reboot Red Pitaya
echo "Rebooting Red Pitaya..."
ssh root@"$RP_IP" "reboot"

echo "Reboot command sent. SSH session will disconnect."
echo ""

# 5. Finished
echo "------------------------------------------------------------"
echo "    LINIEN SERVER DEPLOYMENT COMPLETE"
echo "------------------------------------------------------------"
echo ""