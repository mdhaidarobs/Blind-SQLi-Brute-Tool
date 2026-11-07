#!/usr/bin/env python3
import sys
import subprocess
import os

from colorama import Fore, Style
from tools.common import banner, log_info, log_warn, log_error

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def show_menu():
    banner(subtitle="M A I N   S E L E C T O R   M E N U")
    print(f"{Fore.CYAN}Choose which lab type you want to target:{Style.RESET_ALL}\n")
    print(f"  {Fore.YELLOW}[1]{Style.RESET_ALL}  Boolean-based Blind SQLi  (response contains \"Welcome back\")")
    print(f"  {Fore.YELLOW}[2]{Style.RESET_ALL}  Error-based Blind SQLi    (server returns HTTP 500 / Internal Server Error)")
    print(f"  {Fore.YELLOW}[3]{Style.RESET_ALL}  Time-based Blind SQLi     (pg_sleep / SLEEP / WAITFOR delay)")
    print(f"  {Fore.YELLOW}[98]{Style.RESET_ALL} Help")
    print(f"  {Fore.YELLOW}[99]{Style.RESET_ALL} About")
    print(f"  {Fore.YELLOW}[0]{Style.RESET_ALL}  Exit\n")


def show_help():
    banner(subtitle="H E L P")
    print(f"""
{Fore.CYAN}Usage:{Style.RESET_ALL}
  python3 main.py                          -> interactive menu
  python3 main.py -m1 [args...]            -> Boolean-based engine directly
  python3 main.py -m2 [args...]            -> Error-based engine directly
  python3 main.py -m3 [args...]            -> Time-based engine directly
  python3 main.py -h | --help              -> this help page
  python3 main.py --about                  -> about page

{Fore.CYAN}Common args (all modes):{Style.RESET_ALL}
  -u   <URL>          Target lab URL (required)
  -t   <TRACKING>     Base tracking ID (required)
  -c   <COOKIE_NAME>  Vulnerable cookie name (default: TrackingId)
  -sc  <SESSION>      Session cookie value (optional)
  -usr <USERS>        Comma-separated usernames (default: administrator)
  -l   <LENGTH>       Password length (required, positive integer)
  -db  <DBMS>         auto|mysql|postgres|oracle|mssql|sqlite (default: auto)
  -p   <PROXY>        Proxy URL e.g. http://127.0.0.1:8080
  -w   <WORKERS>      Parallel workers (use 1 for PortSwigger)
  -T   <TIMEOUT>      Request timeout in seconds (default: 15)
  -s                  Include special characters in charset
  -o   <LOGFILE>      Custom log filepath

{Fore.CYAN}Boolean-only:{Style.RESET_ALL}
  --success-indicator <STR>   Success string in response (default: "Welcome back")

{Fore.CYAN}Time-only:{Style.RESET_ALL}
  -d   <DELAY>        Sleep seconds per TRUE condition (default: 10)
  -th  <THRESHOLD>    Elapsed >= threshold => TRUE (default: 7)

{Fore.CYAN}Examples:{Style.RESET_ALL}
  # Boolean
  python3 main.py -m1 -u "https://LAB/filter?category=Gifts" \\
      -t "TRACKING_ID" -sc "SESSION_ID" -l 20 -w 1 -db auto

  # Error (Oracle)
  python3 main.py -m2 -u "https://LAB/filter?category=Gifts" \\
      -t "TRACKING_ID" -sc "SESSION_ID" -l 20 -w 1 -db oracle

  # Time-based (PostgreSQL)
  python3 main.py -m3 -u "https://LAB/filter?category=Gifts" \\
      -t "TRACKING_ID" -sc "SESSION_ID" -l 20 -w 1 -db postgres -d 10 -th 7

Logs are saved under ./logs/
""")


def show_about():
    banner(subtitle="A B O U T")
    print(f"""
{Fore.CYAN}Blind SQLi Brute Tool{Style.RESET_ALL}
Version : 2.1
Purpose : Automate Blind SQL injection exploitation for authorized labs
          (PortSwigger Web Security Academy, HTB, TryHackMe, CTFs).

Engines:
  [1] Boolean-based   - "Welcome back" / custom success indicator
  [2] Error-based     - HTTP 500 / Internal Server Error
  [3] Time-based      - pg_sleep / SLEEP / WAITFOR / DBMS_PIPE

DBMS support (auto-detect or manual):
  MySQL, PostgreSQL, Oracle, MSSQL, SQLite

Author  : Md Haidar
GitHub  : https://github.com/mdhaidarobs
LinkedIn: https://www.linkedin.com/in/haidarobs

{Fore.YELLOW}Disclaimer:{Style.RESET_ALL} For educational and authorized testing only.
The author is not responsible for misuse.
""")


def run_script(rel_path, passthrough):
    path = os.path.join(BASE_DIR, rel_path)
    if not os.path.exists(path):
        log_error(f"Missing file: {rel_path}")
        sys.exit(1)
    cmd = [sys.executable, path] + passthrough
    try:
        subprocess.run(cmd, check=False, cwd=BASE_DIR)
    except KeyboardInterrupt:
        log_warn("\n[!] Interrupted by user.")
        sys.exit(0)


def interactive_select():
    while True:
        show_menu()
        choice = input(f"{Fore.CYAN}Enter your choice [0-3, 98, 99]: {Style.RESET_ALL}").strip()

        if choice == "1":
            log_info("Launching Boolean-based engine...\n")
            run_script(os.path.join("tools", "boolean_sqli.py"), [])
            return
        elif choice == "2":
            log_info("Launching Error-based engine...\n")
            run_script(os.path.join("tools", "error_sqli.py"), [])
            return
        elif choice == "3":
            log_info("Launching Time-based engine...\n")
            run_script(os.path.join("tools", "time_sqli.py"), [])
            return
        elif choice == "98":
            show_help()
        elif choice == "99":
            show_about()
        elif choice == "0":
            log_warn("Exiting.")
            sys.exit(0)
        else:
            log_error("Invalid choice. Please enter 0, 1, 2, 3, 98, or 99.")


def main():
    argv = sys.argv[1:]

    if not argv:
        interactive_select()
        return

    if argv[0] in ("-m1", "--boolean"):
        run_script(os.path.join("tools", "boolean_sqli.py"), argv[1:])
    elif argv[0] in ("-m2", "--error"):
        run_script(os.path.join("tools", "error_sqli.py"), argv[1:])
    elif argv[0] in ("-m3", "--time"):
        run_script(os.path.join("tools", "time_sqli.py"), argv[1:])
    elif argv[0] in ("-h", "--help"):
        show_help()
    elif argv[0] == "--about":
        show_about()
    else:
        log_error(f"Unknown flag: {argv[0]}. Use -h for help.")
        sys.exit(1)


if __name__ == "__main__":
    main()