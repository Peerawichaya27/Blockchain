import json
import random
import string

def generate_hashes(count):
    """Generate a list of random hashes."""
    return [''.join(random.choices(string.ascii_lowercase + string.digits, k=64)) for _ in range(count)]

# Generate datasets
datasets = {
    "10": generate_hashes(10),
    "50": generate_hashes(50),
    "100": generate_hashes(100),
    "250": generate_hashes(250),
    "500": generate_hashes(500),
    "1000": generate_hashes(1000)
}

# Save to JSON files
for size, hashes in datasets.items():
    with open(f"hashes_{size}.json", "w") as file:
        json.dump({"hashes": hashes}, file)
