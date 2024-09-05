import json
import subprocess
from pathlib import Path

CONFIG_TEMPLATE_PATH = Path("config_template.json")
CONFIG_WORKER_TOPIC_CHUNKS_PATH = Path("config_worker_topic_chunk.json")
GITHUB_URLS_PATH = Path("github-urls.json")
MODEL_TYPES = ["meme", "15m", "1d"]  # from github-urls.json (GITHUB_URLS_PATH)

TOPIC_INFO = """
Topic ID        Metadata         Default Arg
  1       ETH 10min Prediction       ETH
  2       ETH 24h Prediction         ETH
  3       BTC 10min Prediction       BTC
  4       BTC 24h Prediction         BTC
  5       SOL 10min Prediction       SOL
  6       SOL 24h Prediction         SOL
  7       ETH 20min Prediction       ETH
  8       BNB 20min Prediction       BNB
  9       ARB 20min Prediction       ARB
 10       Memecoin 1h Prediction   TOKEN_FROM_API
"""

TOPICS_ARGS = {
    "1": "ETH",
    "2": "ETH",
    "3": "BTC",
    "4": "BTC",
    "5": "SOL",
    "6": "SOL",
    "7": "ETH",
    "8": "BNB",
    "9": "ARB",
}

AVAILABLE_10_TOPIC_ARGS = {
    'DOGE': 'DOGEUSDT',
    'BOME': 'BOMEUSDT',
    'BONK': 'BONKUSDT',
    'MEME': 'MEMEUSDT',
    'ORDI': 'ORDIUSDT',
    'FLOKI': 'FLOKIUSDT',
    'PEOPLE': 'PEOPLEUSDT',
    'WIF': 'WIFUSDT',
    '1000SATS': '1000SATSUSDT'
}

AVAILABLE_10_TOPIC_ARGS_LIST = list(AVAILABLE_10_TOPIC_ARGS.keys())


# wget allora.sh script
def load_allora_script():
    pass


def do_command(cmd):
    split_cmd = cmd.split()
    try:
        result = subprocess.run(split_cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return None
    combined_output = result.stdout + result.stderr
    return combined_output


def get_from_input(input_message: str, confirm_message: str, agree: str = "y") -> str:
    while True:
        user_input = input(input_message)
        confirm = input(confirm_message)
        if confirm.lower() == agree:
            return user_input
        else:
            continue


def get_topic_ids():
    print(TOPIC_INFO)
    topic_ids = []
    while True:
        topic_id = input("Enter topic ID (0 to exit): ").strip()
        if topic_id == "0":
            break
        if topic_id not in TOPICS_ARGS.keys() and topic_id != "10":
            print("Invalid topic ID")
            continue

        if topic_id != "10":
            token = TOPICS_ARGS[topic_id]
            topic_ids.append({
                "topic_id": topic_id,
                "arg": token
            })
        else:
            print("Available 10 topic's tokens: ")
            print(" ".join(AVAILABLE_10_TOPIC_ARGS_LIST))
            token = input("Enter token ARG: ")
            if token not in AVAILABLE_10_TOPIC_ARGS_LIST:
                print("Invalid token")
                continue
            topic_ids.append({
                "topic_id": topic_id,
                "arg": token
            })
        print(f"Added topic ID: {topic_id} with token: {token}")

    print("Selected topics: ")
    for topic in topic_ids:
        print(f"Topic ID: {topic['topic_id']} with token: {topic['arg']}")

    return topic_ids


def get_json_from_path(json_path: Path) -> dict | None:
    try:
        with open(json_path, "r") as f:
            config = json.load(f)
        return config
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return None


def get_model_type():
    model_type = None
    print("Available model types: ")
    for i in range(len(MODEL_TYPES)):
        print(f"{i}. {MODEL_TYPES[i]}")
    while True:
        model_type_index = input("Enter model type index: ").strip()
        try:
            model_type_index = int(model_type_index)
        except ValueError:
            print("Invalid model type index")
            continue
        if model_type_index < 0 or model_type_index >= len(MODEL_TYPES):
            print("Invalid model type index")
            continue
        model_type = MODEL_TYPES[model_type_index]
        break
    return model_type


def wget_from_url(url: str, file_name: str = None):
    if file_name is None:
        file_name = url.split("/")[-1]

    wget_command = f"wget -O {file_name} {url}"
    print(wget_command)
    subprocess.call(wget_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(f"Downloaded {file_name} from {url}")
    print()
    return file_name


if __name__ == "__main__":
    # load_allora_command = ("wget https://raw.githubusercontent.com/dxzenith/allora-worker-node/main/allora.sh && chmod "
    #                        "+x allora.sh")
    # do_command(load_allora_command)

    node_ip: str = get_from_input("Enter node ip: ", "Confirm node address (y/n): ").strip()
    rpc_node_url: str = get_from_input("Enter RPC node address: ", "Confirm RPC node address (y/n): ").strip()
    seed: str = get_from_input("Enter seed phrase: ", "Confirm seed phrase (y/n): ").strip()

    model_type = get_model_type()
    github_urls: None | dict = get_json_from_path(GITHUB_URLS_PATH)

    if github_urls is None:
        print("Error: Failed to load github urls")
        exit(1)

    # Load model files from github
    model_urls = github_urls[model_type]
    wget_from_url(model_urls["model_url"], "birnn_model_optimized.pth")
    wget_from_url(model_urls["app_url"], "app.py")
    wget_from_url(model_urls["requirements.txt"], "requirements.txt")

    topics_ids = get_topic_ids()

    print("Node IP:", node_ip)
    print("RPC node address:", rpc_node_url)
    print("Seed phrase:", seed)
    print("Selected topics: ")
    for topic in topics_ids:
        print(f"Topic ID: {topic['topic_id']} with token: {topic['arg']}")

    input("Press Enter to continue...")

    config: None | dict = get_json_from_path(CONFIG_TEMPLATE_PATH)
    if config is None:
        print("Error: Failed to load config template")
        exit(1)

    config["wallet"]["addressRestoreMnemonic"] = seed
    config["wallet"]["nodeRpc"] = rpc_node_url

    worker_chunk: None | dict = get_json_from_path(CONFIG_WORKER_TOPIC_CHUNKS_PATH)
    if worker_chunk is None:
        print("Error: Failed to load worker chunk config")
        exit(1)

    worker_chunks = []
    for topic in topics_ids:
        worker_chunk: None | dict = get_json_from_path(CONFIG_WORKER_TOPIC_CHUNKS_PATH)
        if worker_chunk is None:
            print("Error: Failed to load worker chunk config")
            exit(1)
        worker_chunk["topicId"] = int(topic["topic_id"])
        worker_chunk["parameters"]["Token"] = topic["arg"]
        worker_chunk["parameters"]["InferenceEndpoint"] = f"http://{node_ip}:8000/inference/" + "{Token}"
        worker_chunks.append(worker_chunk)

    config["worker"] = worker_chunks

    with open("config.json", "w") as f:
        json.dump(config, f, indent=2)
