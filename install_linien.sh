#!/bin/bash

# ------------------------------------------------------------
#     LINIEN CLIENT INSTALLATION (macOS bash version)
# ------------------------------------------------------------

# ------------------------------
# CONFIGURATION (EDIT THIS PATH)
# ------------------------------
VENV="/Users/jeffreyli/Desktop/Ni Lab/oldlinienvenv"
# ------------------------------

echo "------------------------------------------------------------"
echo "    LINIEN CLIENT INSTALLATION"
echo "------------------------------------------------------------"
echo ""

# 1. Check that the virtual environment exists
if [ ! -f "$VENV/bin/python" ]; then
    echo "ERROR: Virtual environment not found at:"
    echo "       $VENV"
    echo ""
    echo "Create it first using:"
    echo "    python3 -m venv \"$VENV\""
    exit 1
fi

echo "Virtual environment found:"
echo "    $VENV"
echo ""

PYTHON="$VENV/bin/python"

# 2. Install GUI-dependent packages
echo "Installing GUI requirements..."
"$PYTHON" -m pip install --no-deps -r requirements_gui
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install GUI requirements."
    exit 1
fi
echo ""

# 3. Install GUI component
echo "Installing Linien GUI..."
"$PYTHON" setup_gui.py install
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install setup_gui.py"
    exit 1
fi
echo ""

# 4. Install client component
echo "Installing Linien client..."
"$PYTHON" setup_client.py install
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install setup_client.py"
    exit 1
fi
echo ""

# Finished
echo "------------------------------------------------------------"
echo "    LINIEN CLIENT INSTALLATION COMPLETE"
echo "------------------------------------------------------------"
echo ""

exit 0