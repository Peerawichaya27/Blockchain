import hashlib

# Employer's unhashed email
email = "hr123@gmail.com"

# Hash the email using SHA-256
hashed_email = hashlib.sha256(email.encode()).hexdigest()

print(hashed_email)
