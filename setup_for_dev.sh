#!/usr/bin/env bash

command -v pyenv >/dev/null 2>&1 || { echo "Installing pyenv" >&2; brew install pyenv; }

echo "-> Installing python from .python-version with pyenv <-"
pyenv install

eval "$(pyenv init -)"

pip install virtualenv

echo "-> Creating virtualenv..."
virtualenv --setuptools --no-site-packages --prompt="(${PWD##*/}) " -p python3 .venv

echo "-> Activating virtualenv..."
source .venv/bin/activate

echo "Upgrading and installing pip dependencies..."
pip install -r requirements.txt
deactivate
echo "-> Pip dependencies install complete!"

echo "Done!"