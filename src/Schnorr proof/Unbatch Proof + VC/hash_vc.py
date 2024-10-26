import json
import hashlib
import os  # To check if the file exists

# Function to hash the Verifiable Credential (VC)
def hash_verifiable_credential(vc):
    # Convert the VC dictionary to a JSON string
    vc_string = json.dumps(vc, separators=(',', ':'))  # Ensure consistent string formatting
    return hashlib.sha256(vc_string.encode()).hexdigest()

# Function to store the hashed VCs along with student DID in ipfs.json
def store_hashed_vcs(vcs):
    # Check if the file exists or is empty, if not create an empty dictionary
    if not os.path.exists('ipfs.json') or os.stat('ipfs.json').st_size == 0:
        ipfs_data = {}
    else:
        # Load the existing ipfs.json file
        with open('ipfs.json', 'r') as file:
            ipfs_data = json.load(file)

    # Add or update the hashed VCs and student DIDs under their respective indices
    for index, vc_data in vcs.items():
        ipfs_data[str(index)] = vc_data

    # Save the updated data back to ipfs.json
    with open('ipfs.json', 'w') as file:
        json.dump(ipfs_data, file, indent=4)

    print(f"{len(vcs)} Hashed VCs stored successfully in ipfs.json.")

# Function to generate multiple VCs
def generate_vcs(num_vcs):
    vcs = {}
    for i in range(1, num_vcs + 1):
        student_did = f"did:university:student{i}"
        student_vc = {
            "@context": [
                "https://www.w3.org/2018/credentials/v1"
            ],
            "id": f"http://university.edu/credentials/student-credential-{i}",
            "type": [
                "VerifiableCredential",
                "StudentCredential"
            ],
            "issuer": "did:university:issuer123",
            "issuanceDate": "2024-09-25T19:23:24Z",
            "credentialSubject": {
                "id": student_did,
                "name": f"Student {i}"
            },
            "proof": {
                "type": "Ed25519Signature2020",
                "created": "2024-09-25T20:10:10Z",
                "proofPurpose": "assertionMethod",
                "verificationMethod": "did:university:issuer123#key-1",
                "jws": "eyJhbGciOiJFZERTQSJ9.eyJAY29udGV4dCI6IFsiaHR0cHM6Ly93d3cudzMub3JnLzIwMTgvY3JlZGVudGlhbHMvdjEiXSwgImlkIjogImh0dHA6Ly91bml2ZXJzaXR5LmVkdS9jcmVkZW50aWFscy9zdHVkZW50LWNyZWRlbnRpYWwtMTIzIiwgInR5cGUiOiBbIlZlcmlmaWFibGVDcmVkZW50aWFsIiwgIlN0dWRlbnRDcmVkZW50aWFsIl0sICJpc3N1ZXIiOiAiZGlkOnVuaXZlcnNpdHk6aXNzdWVyMTIzIiwgImlzc3VhbmNlRGF0ZSI6ICIyMDI0LTA5LTI1VDE5OjIzOjI0WiIsICJjcmVkZW50aWFsU3ViamVjdCI6IHsiaWQiOiAiZGlkOnVuaXZlcnNpdHk6c3R1ZGVudDEyMyIsICJuYW1lIjogIkpvaG4gRG9lIn19.Nnc447eCRJgDmUMpHC3FS6F6xoX4HITi79V9pDPwBnVb096Xh2xxjmdgLN4GFjOMX8jcU5BLsg3UcfAnKbWZCw"
            }
        }

        # Hash the VC and store in the dictionary
        hashed_vc = hash_verifiable_credential(student_vc)

        # Store both the hashed VC and the student's DID
        vcs[i] = {
            "student_did": student_did,
            "hashed_vc": hashed_vc
        }

    return vcs

# Example usage
def main():
    num_vcs = int(input("Enter the number of VCs to generate: "))

    # Generate the VCs and their hashed values
    vcs = generate_vcs(num_vcs)

    # Store the hashed VCs and DIDs in ipfs.json
    store_hashed_vcs(vcs)

if __name__ == "__main__":
    main()
