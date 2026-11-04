#!/usr/bin/env python3
import sys
import subprocess
import os

from colorama import Fore, Style
from common import banner, log_info, log_warn, log_error

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def show_menu():
    banner(subtitle="M A I N   S E L E C T O R   M E N U")
    print(f"{Fore.CYAN}Choose which lab type you want to target:{Style.RESET_ALL}\n")
    print(f"  {Fore.YELLOW}[1]{Style.RESET_ALL} Boolean-based Blind SQLi  (response contains \"Welcome back\")")
    print(f"  {Fore.YELLOW}[2]{Style.RESET_ALL} Error-based Blind SQLi    (server returns HTTP 500 / Internal Server Error)")
    print(f"  {Fore.YELLOW}[3]{Style.RESET_ALL} Exit\n")


def run_script(filename, passthrough):
    path = os.path.join(BASE_DIR, filename)
    if not os.path.exists(path):
        log_error(f"Missing file: {filename}")
        sys.exit(1)
    cmd = [sys.executable, path] + passthrough
    try:
        subprocess.run(cmd, check=False)
    except KeyboardInterrupt:
        log_warn("\n[!] Interrupted by user.")
        sys.exit(0)


def interactive_select(passthrough):
    while True:
        show_menu()
        choice = input(f"{Fore.CYAN}Enter your choice [1-3]: {Style.RESET_ALL}").strip()

        if choice == "1":
            log_info("Launching Boolean-based engine...\n")
            run_script("boolean_sqli.py", passthrough)
            return
        elif choice == "2":
            log_info("Launching Error-based engine...\n")
            run_script("error_sqli.py", passthrough)
            return
        elif choice == "3":
            log_warn("Exiting.")
            sys.exit(0)
        else:
            log_error("Invalid choice. Please enter 1, 2, or 3.")


def main():
    argv = sys.argv[1:]

    if not argv:
        interactive_select([])
        return

    if argv[0] in ("-m1", "--boolean"):
        run_script("boolean_sqli.py", argv[1:])
    elif argv[0] in ("-m2", "--error"):
        run_script("error_sqli.py", argv[1:])
    elif argv[0] in ("-h", "--help"):
        banner(subtitle="M A I N   H E L P")
        print(f"""
Usage:
  python3 main.py                          -> interactive menu (choose 1 or 2)
  python3 main.py -m1 [args...]            -> run Boolean-based engine directly
  python3 main.py -m2 [args...]            -> run Error-based engine directly

Example (Boolean):
  python3 main.py -m1 -u "https://lab/filter?category=Gifts" \\
      -t "TRACKING_ID" -sc "SESSION_ID" -l 20 -w 1

Example (Error):
  python3 main.py -m2 -u "https://lab/filter?category=Gifts" \\
      -t "TRACKING_ID" -sc "SESSION_ID" -l 20 -w 1
""")
        sys.exit(0)
    else:
        log_error(f"Unknown flag: {argv[0]}. Use -h for help.")
        sys.exit(1)


if __name__ == "__main__":
    main()