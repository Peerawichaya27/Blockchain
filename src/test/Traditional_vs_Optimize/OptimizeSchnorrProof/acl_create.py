import json
import hashlib

student_did_li = []

# Function to generate ACL entries
def generate_acl(num_entries):
    acl_list = []
    email = "hr1@gamil.com".lower().strip()  # Fixed email for all students
    hashed_email = hashlib.sha256(email.encode()).hexdigest()  # Hash the fixed email

    for i in range(num_entries):
        # Generate student DID in the format did:university:studentXXX
        student_did = f"did:university:student{i+1}"  # DID format with incrementing student numbers

        acl_entry = {
            "student_did": student_did,
            "employer_hashed_email": hashed_email,  # Same hashed email for all entries
            "expiration": 1687581600 + i * 1000,  # Example expiration times (incremented)
            "isValid": True
        }

        student_did_li.append(student_did)
        acl_list.append(acl_entry)

    # Save ACL entries to acl.json
    with open('acl.json', 'w') as acl_file:
        json.dump({"students": acl_list}, acl_file, indent=4)

    print(f"{num_entries} ACL entries successfully created and stored in acl.json.")

# Function to create a batch verification payload
def create_batch_verification_payload(num_entries):
    students = []
    email = "hr1@gmail.com".lower().strip()  # Fixed email for all entries

    for i in range(num_entries):
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
