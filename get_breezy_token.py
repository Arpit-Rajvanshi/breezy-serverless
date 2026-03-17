import httpx
import getpass
import sys

def main():
    print("=== Breezy HR Token Generator ===\n")
    print("This script will hit the /signin endpoint to generate your Personal Access Token.\n")
    
    email = input("Enter your Breezy HR email: ").strip()
    if not email:
        print("Email is required.")
        sys.exit(1)
        
    password = getpass.getpass("Enter your Breezy HR password: ")
    if not password:
        print("Password is required.")
        sys.exit(1)
        
    print("\nAuthenticating with Breezy HR...")
    try:
        response = httpx.post(
            "https://api.breezy.hr/v3/signin", 
            json={"email": email, "password": password},
            timeout=10.0
        )
        
        if response.is_success:
            data = response.json()
            access_token = data.get("access_token")
            user = data.get("user", {})
            
            print("\n✅ Authentication Successful!")
            print("-" * 50)
            print(f"Your BREEZY_API_KEY: {access_token}")
            print("-" * 50)
            print("Copy the token above and paste it into your .env file as BREEZY_API_KEY.")
            
            # Since we have the token, let's also try to fetch the Company ID to make it easy
            print("\nFetching your Company ID...")
            comp_response = httpx.get(
                "https://api.breezy.hr/v3/companies",
                headers={"Authorization": access_token},
                timeout=10.0
            )
            
            if comp_response.is_success:
                companies = comp_response.json()
                if companies and isinstance(companies, list):
                    print("\nFound the following companies:")
                    for idx, comp in enumerate(companies):
                        comp_name = comp.get("name", "Unknown")
                        comp_id = comp.get("_id", comp.get("id"))
                        print(f"  {idx + 1}. {comp_name} -> BREEZY_COMPANY_ID: {comp_id}")
                    print("\nCopy the appropriate Company ID into your .env file as BREEZY_COMPANY_ID.")
            
        else:
            print(f"\n❌ Failed to authenticate. Status Code: {response.status_code}")
            try:
                err_data = response.json()
                print(f"Error: {err_data.get('message', err_data)}")
            except:
                print(f"Response: {response.text}")
                
    except Exception as e:
        print(f"\n❌ An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
