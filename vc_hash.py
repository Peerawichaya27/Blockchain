import hashlib

# Example student ID (VC)
student_id = "123456789"

# Compute the SHA256 hash of the student ID
vc_hash = hashlib.sha256(student_id.encode()).hexdigest()

print(f"0x{vc_hash}")
