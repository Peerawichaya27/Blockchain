import json
import hashlib
import time

student_did_list = []

# Function to generate ACL entries
def generate_acl(num_entries):
    acl_list = []
    email_template = "hr{}@gmail.com".lower().strip()  # Dynamic email template

    for i in range(num_entries):
        # Generate unique email and hash it
        email = email_template.format(1)
        hashed_email = hashlib.sha256(email.encode()).hexdigest()

        # Generate student DID
        student_did = f"did:university:student{i+1}"

        # Generate human-readable expiration (current time + offset)
        expiration = int(time.time()) + (i * 1000)

        # Define selective disclosure fields
        selective_disclosure = ["religion", "sex"]

        acl_entry = {
            "student_did": student_did,
            "employer_hashed_email": hashed_email,
            "selective_disclosure": selective_disclosure,
            "expiration": expiration,
            "isValid": True
        }

        student_did_list.append(student_did)
        acl_list.append(acl_entry)

    # Save ACL entries to acl.json
    with open('acl.json', 'w') as acl_file:
        json.dump({"students": acl_list}, acl_file, indent=4)

    print(f"{num_entries} ACL entries successfully created and stored in acl.json.")

# Main function to run the program
def main():
    while True:
        try:
            num_entries = int(input("Enter the number of ACL entries to create: "))
            if num_entries <= 0:
                raise ValueError("The number of entries must be a positive integer.")
            break
        except ValueError as e:
            print(f"Invalid input: {e}. Please try again.")

    # Generate ACL entries
    generate_acl(num_entries)

if __name__ == "__main__":
    main()
