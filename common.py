#!/usr/bin/env python3
import sys
import string
import logging
from datetime import datetime
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

def setup_logger(log_file, name="BlindSQLiPro"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    for h in list(logger.handlers):
        logger.removeHandler(h)

    fh = logging.FileHandler(log_file, mode='w', encoding='utf-8')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter('%(message)s'))

    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger

def banner(title="B L I N D   S Q L I   P R O", subtitle="", version="3.7"):
    print(f"""
{Fore.CYAN}
    ====================================================================
                {title}
                {subtitle}
    ====================================================================
    [+] Creator   : M Haidar
    [+] LinkedIn  : https://www.linkedin.com/in/haidarobs
    [+] GitHub    : https://github.com/mdhaidarobs
    [+] Version   : {version}
    ====================================================================
{Style.RESET_ALL}
    """)

def log_info(msg, color=Fore.GREEN):
    print(f"{color}[+]{Style.RESET_ALL} {msg}")

def log_warn(msg, color=Fore.YELLOW):
    print(f"{color}[!]{Style.RESET_ALL} {msg}")

def log_error(msg, color=Fore.RED):
    print(f"{color}[-]{Style.RESET_ALL} {msg}")

def build_charset(use_special=False):
    charset = string.ascii_lowercase + string.ascii_uppercase + string.digits
    if use_special:
        charset += "!@#$%^&*()-_=+[]{}|;:,.<>?/\\~`"
    return charset

def make_session(retries=3):
    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(max_retries=retries)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def make_proxies(proxy):
    if not proxy:
        return None
    return {'http': proxy, 'https': proxy}

def timestamp_log_name(prefix="sqli"):
    return f"{prefix}_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

def prompt_url():
    while True:
        url = input(f"{Fore.CYAN}Enter Target Lab URL (e.g., https://example.com/filter?category=Gifts): {Style.RESET_ALL}").strip()
        if url.startswith("http"):
            return url
        log_error("URL must start with http:// or https://. Try again.")

def prompt_tracking():
    while True:
        t = input(f"{Fore.CYAN}Enter your Base Tracking ID value: {Style.RESET_ALL}").strip()
        if t:
            return t
        log_error("Tracking ID cannot be empty. Try again.")

def prompt_cookie_name():
    c = input(f"{Fore.CYAN}Enter Cookie Name vulnerable to SQLi [Default: TrackingId]: {Style.RESET_ALL}").strip()
    return c if c else "TrackingId"

def prompt_session_cookie():
    s = input(f"{Fore.CYAN}Enter Session Cookie value (leave blank if none): {Style.RESET_ALL}").strip()
    return s if s else None

def prompt_users():
    u = input(f"{Fore.CYAN}Enter Username(s) to target (comma separated) [Default: administrator]: {Style.RESET_ALL}").strip()
    return u if u else "administrator"

def prompt_length():
    v = input(f"{Fore.CYAN}Enter expected password length (e.g., 20) or leave blank for auto-detect: {Style.RESET_ALL}").strip()
    if v:
        try:
            n = int(v)
            if n > 0:
                return n
        except ValueError:
            pass
        log_warn("Invalid length. Auto-detection will be used.")
    return None

def prompt_proxy():
    use = input(f"{Fore.CYAN}Route traffic through Burp Suite proxy (127.0.0.1:8080)? (y/N): {Style.RESET_ALL}").strip().lower()
    if use == 'y':
        log_info("Proxy enabled: Traffic will route through Burp Suite.")
        return "http://127.0.0.1:8080"
    return None

def prompt_workers(default=1):
    w = input(f"{Fore.CYAN}Enter number of workers [Default: {default}, use 1 for PortSwigger]: {Style.RESET_ALL}").strip()
    if w:
        try:
            n = int(w)
            return max(1, n)
        except ValueError:
            pass
    return default

def prompt_special():
    s = input(f"{Fore.CYAN}Include special characters in charset? (y/N): {Style.RESET_ALL}").strip().lower()
    return s == 'y'

def prompt_timeout(default=15):
    t = input(f"{Fore.CYAN}Enter request timeout in seconds [Default: {default}]: {Style.RESET_ALL}").strip()
    if t:
        try:
            return max(1, int(t))
        except ValueError:
            pass
    return default