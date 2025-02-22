#!/bin/bash

BOLD="\033[1m"
UNDERLINE="\033[4m"
DARK_YELLOW="\033[0;33m"
CYAN="\033[0;36m"
GREEN="\033[0;32m"
RESET="\033[0m"

execute_with_prompt() {
    echo -e "${BOLD}Executing: $1${RESET}"
    if eval "$1"; then
        echo "Command executed successfully."
    else
        echo -e "${BOLD}${DARK_YELLOW}Error executing command: $1${RESET}"
        exit 1
    fi
}

echo -e "${BOLD}${UNDERLINE}${DARK_YELLOW}Requirement for running allora-worker-node${RESET}"
echo
echo -e "${BOLD}${DARK_YELLOW}Operating System : Ubuntu 22.04${RESET}"
echo -e "${BOLD}${DARK_YELLOW}CPU : Min of 1/2 core.${RESET}"
echo -e "${BOLD}${DARK_YELLOW}RAM : 2 to 4 GB.${RESET}"
echo -e "${BOLD}${DARK_YELLOW}Storage : SSD or NVMe with at least 5GB of space.${RESET}"
echo

echo -e "${CYAN}Do you meet all of these requirements? (Y/N):${RESET}"
read -p "" response
echo

if [[ ! "$response" =~ ^[Yy]$ ]]; then
    echo -e "${BOLD}${DARK_YELLOW}Error: You do not meet the required specifications. Exiting...${RESET}"
    echo
    exit 1
fi

echo -e "${BOLD}${DARK_YELLOW}Updating system dependencies...${RESET}"
execute_with_prompt "sudo apt update -y && sudo apt upgrade -y"
echo

echo -e "${BOLD}${DARK_YELLOW}Installing jq packages...${RESET}"
execute_with_prompt "sudo apt install jq"
echo

#echo -e "${BOLD}${DARK_YELLOW}Installing Docker...${RESET}"
#execute_with_prompt 'curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg'
echo
execute_with_prompt 'echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null'
echo
execute_with_prompt 'sudo apt-get update'
echo
execute_with_prompt 'sudo apt-get install docker-ce docker-ce-cli containerd.io -y'
echo
sleep 2
echo -e "${BOLD}${DARK_YELLOW}Checking docker version...${RESET}"
execute_with_prompt 'docker version'
echo

echo -e "${BOLD}${DARK_YELLOW}Installing Docker Compose...${RESET}"
VER=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep tag_name | cut -d '"' -f 4)
echo
execute_with_prompt 'sudo curl -L "https://github.com/docker/compose/releases/download/'"$VER"'/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose'
echo
execute_with_prompt 'sudo chmod +x /usr/local/bin/docker-compose'
echo

echo -e "${BOLD}${DARK_YELLOW}Checking docker-compose version...${RESET}"
execute_with_prompt 'docker-compose --version'
echo

if ! grep -q '^docker:' /etc/group; then
    execute_with_prompt 'sudo groupadd docker'
    echo
fi

execute_with_prompt 'sudo usermod -aG docker $USER'
echo
echo -e "${GREEN}${BOLD}Request faucet to your wallet from this link:${RESET} https://faucet.testnet-1.testnet.allora.network/"
echo

echo -e "${BOLD}${UNDERLINE}${DARK_YELLOW}Installing worker node...${RESET}"
git clone https://github.com/allora-network/basic-coin-prediction-node
echo
cd basic-coin-prediction-node
echo
mkdir worker-data

wget https://raw.githubusercontent.com/darya-ch-boop/models/main/init_worker/docker-compose.yml -O docker-compose.yml
wget https://raw.githubusercontent.com/darya-ch-boop/models/main/init_worker/config_template.json
wget https://raw.githubusercontent.com/darya-ch-boop/models/main/init_worker/config_worker_topic_chunk.json
wget https://raw.githubusercontent.com/darya-ch-boop/models/main/init_worker/github-urls.json
wget https://raw.githubusercontent.com/darya-ch-boop/models/main/init_worker/init_worker.py

python3 init_worker.py


chmod +x init.config
sleep 2
./init.config

# **Открыть порт 8000**
echo -e "${BOLD}${UNDERLINE}${DARK_YELLOW}Open port 8000..."${RESET}"
iptables -P INPUT ACCEPT
iptables -P OUTPUT ACCEPT
iptables -P FORWARD ACCEPT
iptables -F

ufw allow from any to 127.0.0.1 port 8000 && \
ufw allow to any from 127.0.0.1 port 8000 && \
ufw status

echo
echo -e "${BOLD}${UNDERLINE}${DARK_YELLOW}Pulling Docker containers..."${RESET}"
docker compose pull
echo

echo
echo -e "${BOLD}${UNDERLINE}${DARK_YELLOW}Building and starting Docker containers...${RESET}"
docker compose build
docker-compose up -d
echo
sleep 2
echo -e "${BOLD}${DARK_YELLOW}Checking running Docker containers...${RESET}"
docker ps
echo
execute_with_prompt 'docker logs -f worker'
echo
