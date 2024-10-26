import json
import hashlib
import random
from datetime import datetime, timedelta

student_did_li = []

# Function to generate ACL entries
def generate_acl(num_entries):
    acl_list = []

    # Get the current time and add 2 days (in seconds)
    current_time = datetime.now()
    expiration_time = current_time + timedelta(days=2)
    expiration_timestamp = int(expiration_time.timestamp())  # Convert to Unix timestamp

    for i in range(num_entries):
        # Generate student DID in the format did:university:studentXXX
        student_did = f"did:university:student{i+1}"  # DID format with incrementing student numbers
        email = f"hr{i+1}@gmail.com".lower().strip()  # Generate employer email
        hashed_email = hashlib.sha256(email.encode()).hexdigest()  # Hash the email

        acl_entry = {
            "student_did": student_did,
            "employer_hashed_email": hashed_email,
            "expiration": expiration_timestamp,  # Set expiration to current + 2 days
            "isValid": True
        }

        student_did_li.append(student_did)
        acl_list.append(acl_entry)

    # Save ACL entries to acl.json
    with open('acl.json', 'w') as acl_file:
        json.dump({"students": acl_list}, acl_file, indent=4)

    print(f"{num_entries} ACL entries successfully created and stored in acl.json with expiration in 2 days.")

# Function to create a batch verification payload
def create_batch_verification_payload(num_entries):
    students = []

    for i in range(num_entries):
        email = f"hr{i+1}@gmail.com".lower().strip()  # Generate employer email

        # Add student DID and unhashed email for batch verification
        students.append({
            "email": email,
            "student_did": student_did_li[i]  # Use the custom student DID from the ACL list
        })

    # Save the batch verification payload to a JSON file
    with open('batch_verification_payload.json', 'w') as batch_file:
        json.dump({"students": students}, batch_file, indent=4)

    print(f"Batch verification payload with {num_entries} entries successfully created in batch_verification_payload.json.")

# Main function to run the program
def main():
    num_entries = int(input("Enter the number of ACL entries to create: "))
    
    # Generate ACL entries
    generate_acl(num_entries)

    # Generate batch verification payload
    create_batch_verification_payload(num_entries)

if __name__ == "__main__":
    main()
