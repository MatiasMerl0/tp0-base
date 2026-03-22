import sys
import yaml


def generate_compose(output_file, num_clients):
    services = {}

    services["server"] = {
        "container_name": "server",
        "image": "server:latest",
        "entrypoint": "python3 /main.py",
        "environment": [
            "PYTHONUNBUFFERED=1",
            "LOGGING_LEVEL=DEBUG",
        ],
        "networks": ["testing_net"],
    }

    for i in range(1, num_clients + 1):
        services[f"client{i}"] = {
            "container_name": f"client{i}",
            "image": "client:latest",
            "entrypoint": "/client",
            "environment": [
                f"CLI_ID={i}",
                "CLI_LOG_LEVEL=DEBUG",
            ],
            "networks": ["testing_net"],
            "depends_on": ["server"],
        }

    compose = {
        "name": "tp0",
        "services": services,
        "networks": {
            "testing_net": {
                "ipam": {
                    "driver": "default",
                    "config": [{"subnet": "172.25.125.0/24"}],
                }
            }
        },
    }

    with open(output_file, "w") as f:
        yaml.dump(compose, f, default_flow_style=False, sort_keys=False)


if __name__ == "__main__":
    output_file = sys.argv[1]

    if not sys.argv[2].isdigit() or int(sys.argv[2]) < 1:
        print("Error: la cantidad de clientes debe ser un numero mayor a cero")
        sys.exit(1)

    num_clients = int(sys.argv[2])
    generate_compose(output_file, num_clients)
