import hashlib
import json

# Example ACL data
acl_data = {
  "email": "example@example.com",
  "selective_disclosure": ["religion", "sex"],
  "expiration_time": "2024-09-22T12:00:00",
  "max_verifiers": 3
}

# Convert ACL to string and compute the SHA256 hash
acl_string = json.dumps(acl_data)
acl_hash = hashlib.sha256(acl_string.encode()).hexdigest()

print(f"ACL Hash: {acl_hash}")
