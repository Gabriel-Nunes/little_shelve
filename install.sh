#/bin/bash

<<<<<<< HEAD
=======
cd little_shelve/
>>>>>>> dev
sudo apt-get update && sudo apt-get install docker docker-compose
python3.8 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements-dev.txt
echo export DJANGOSECRETKEY=$(python -c "import secrets; print(secrets.token_urlsafe())") >> ~/.bashrc
source ~/.bashrc
