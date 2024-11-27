import json

# Function to load ACL data from acl.json
def load_acl_data():
    with open('acl.json', 'r') as acl_file:
        acl_data = json.load(acl_file)
    return acl_data['students']

# Function to load hashed VCs from ipfs.json
def load_hashed_vcs():
    with open('ipfs.json', 'r') as ipfs_file:
        ipfs_data = json.load(ipfs_file)
    return ipfs_data

# Verifiable Presentation template
def generate_vp(hashed_vc, student_did):
    vp = {
        "@context": [
            "https://www.w3.org/2018/credentials/v1"
        ],
        "type": "VerifiablePresentation",
        "verifiableCredential": [
            {
                "hash": hashed_vc,  # Include the hashed VC here
                "@context": [
                    "https://www.w3.org/2018/credentials/v1"
                ],
                "id": "http://university.edu/credentials/student-credential-123",
                "type": [
                    "VerifiableCredential",
                    "StudentCredential"
                ],
                "issuer": "did:university:issuer123",
                "issuanceDate": "2024-09-25T19:23:24Z",
                "credentialSubject": {
                    "id": student_did,
                    "name": "John Doe"  # Customize per student
                },
                "proof": {
                    "type": "Ed25519Signature2020",
                    "created": "2024-09-25T20:10:10Z",
                    "proofPurpose": "assertionMethod",
                    "verificationMethod": "did:university:issuer123#key-1",
                    "jws": "eyJhbGciOiJFZERTQSJ9.eyJAY29udGV4dCI6IFsiaHR0cHM6Ly93d3cudzMub3JnLzIwMTgvY3JlZGVudGlhbHMvdjEiXSwgImlkIjogImh0dHA6Ly91bml2ZXJzaXR5LmVkdS9jcmVkZW50aWFscy9zdHVkZW50LWNyZWRlbnRpYWwtMTIzIiwgInR5cGUiOiBbIlZlcmlmaWFibGVDcmVkZW50aWFsIiwgIlN0dWRlbnRDcmVkZW50aWFsIl0sICJpc3N1ZXIiOiAiZGlkOnVuaXZlcnNpdHk6aXNzdWVyMTIzIiwgImlzc3VhbmNlRGF0ZSI6ICIyMDI0LTA5LTI1VDE5OjIzOjI0WiIsICJjcmVkZW50aWFsU3ViamVjdCI6IHsiaWQiOiAiZGlkOnVuaXZlcnNpdHk6c3R1ZGVudDEyMyIsICJuYW1lIjogIkpvaG4gRG9lIn19.Nnc447eCRJgDmUMpHC3FS6F6xoX4HITi79V9pDPwBnVb096Xh2xxjmdgLN4GFjOMX8jcU5BLsg3UcfAnKbWZCw"
                }
            }
        ],
        "proof": {
            "type": "Ed25519Signature2020",
            "created": "2024-09-28T23:51:46+0700",
            "proofPurpose": "authentication",
            "verificationMethod": f"{student_did}#key-1",
            "challenge": "1f44d55f-f161-4938-a659-f8026467f126",
            "domain": "university.edu",
            "jws": "eyJhbGciOiJFZERTQSJ9.eyJAY29udGV4dCI6IFsiaHR0cHM6Ly93d3cudzMub3JnLzIwMTgvY3JlZGVudGlhbHMvdjEiXSwgInR5cGUiOiAiVmVyaWZpYWJsZVByZXNlbnRhdGlvbiIsICJ2ZXJpZmlhYmxlQ3JlZGVudGlhbCI6IFtudWxsXSwgInByb29mIjogeyJ0eXBlIjogIkVkMjU1MTlTaWduYXR1cmUyMDIwIiwgImNyZWF0ZWQiOiAiMjAyNC0wOS0yOFQyMzo1MTo0NiswNzAwIiwgInByb29mUHVycG9zZSI6ICJhdXRoZW50aWNhdGlvbiIsICJ2ZXJpZmljYXRpb25NZXRob2QiOiAiZGlkOnVuaXZlcnNpdHk6c3R1ZGVudDEyMyNrZXktMSIsICJjaGFsbGVuZ2UiOiAiMWY0NGQ1NWYtZjE2MS00OTM4LWE2NTktZjgwMjY0NjdmMTI2IiwgImRvbWFpbiI6ICJ1bml2ZXJzaXR5LmVkdSJ9fQ.oM3cSTmQ_JgkBztWzk9KwZZHX8LMoNIgn2_ozfkKvYMOyqJYBpYQidGd1f6gpptt2qtVosdU9ZMECMl_RWbTAQ"
        }
    }
    return vp

# Function to generate the hashed VC and store the token.json data
def store_token_vp(acl_data, ipfs_data):
    tokens = {}
    for index, student in enumerate(acl_data):
        student_did = student['student_did']
        
        # Get the hashed VC from ipfs.json
        hashed_vc = ipfs_data.get(str(index + 1), {}).get('hashed_vc', None)

        if hashed_vc:
            # Create a Verifiable Presentation (VP)
            vp = generate_vp(hashed_vc, student_did)

            # Store the ACL and VP in the token.json format
            tokens[index + 1] = {
                "student_did": student_did,
                "acl": student,
                "verifiablePresentation": vp
            }

    # Save to token.json
    with open('token.json', 'w') as token_file:
        json.dump(tokens, token_file, indent=4)

    print("Token data with ACL and VP successfully created in token.json.")


if __name__ == "__main__":
    acl_data = load_acl_data()  # Load ACL from acl.json
    ipfs_data = load_hashed_vcs()  # Load hashed VCs from ipfs.json
    store_token_vp(acl_data, ipfs_data)    # Store the ACL and VP in token.json
