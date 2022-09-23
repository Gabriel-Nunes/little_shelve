#/bin/bash

sudo apt-get update && sudo apt-get install docker docker-compose
python3.8 -m venv venv
sleep 3
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements-dev.txt
echo export DJANGOSECRETKEY=$(python -c "import secrets; print(secrets.token_urlsafe())") >> ~/.bashrc
source ~/.bashrc
