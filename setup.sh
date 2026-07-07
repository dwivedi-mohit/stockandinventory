#!/bin/bash

echo "Updating system..."
sudo apt update

echo "Installing Python tools..."
sudo apt install -y python3 python3-pip python3-venv

echo "Creating virtual environment..."
python3 -m venv venv

echo "Activating virtual environment..."
source venv/bin/activate

echo "Upgrading pip..."
python -m pip install --upgrade pip

echo "Installing required packages..."
pip install mysql-connector-python

echo "Checking installations..."
python --version
pip --version

echo "Setup completed successfully!"