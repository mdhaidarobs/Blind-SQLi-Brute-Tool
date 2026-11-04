# Blind-SQLi-Brute-Tool

A command-line tool to automate Blind SQL Injection vulnerability exploitation.

<p><a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.x-blue.svg" alt="Python Version"></a><a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="MIT License"></a><a href="https://github.com/mdhaidarobs"><img src="https://img.shields.io/badge/Author-Md%20Haidar-orange.svg" alt="Author"></a></p>

<p>A lightweight, powerful, and interactive Command-Line Interface (CLI) tool designed to automate <b>Blind SQL Injection</b> testing across both <b>Boolean-based (Conditional Responses)</b> and <b>Error-based (Oracle conditional errors)</b> scenarios. Built for security enthusiasts, penetration testers, and CTF players to practice database security testing in authorized environments such as PortSwigger Web Security Academy.</p>

<hr>

<h2>Tool Screenshots</h2>

<p><i>Here is a quick preview of the tool in action:</i></p>

<img width="1920" height="1080" alt="Screenshot_2026-11-02_23_30_07" src="https://github.com/user-attachments/assets/fd8ee8b5-07d6-4669-acc6-23c50fd4c94b" />

<hr>

<h2>Features & Benefits</h2>

<ul>
  <li><b>Dual Injection Engines:</b> Dedicated modules for Boolean-based (response contains "Welcome back") and Error-based (HTTP 500 / Oracle <code>TO_CHAR(1/0)</code>) Blind SQLi.</li>
  <li><b>Smart Selector Menu:</b> Launch <code>main.py</code> to pick the correct engine interactively, or call it directly via <code>-m1</code> / <code>-m2</code> flags.</li>
  <li><b>Interactive CLI Wizard:</b> Full user control over URL, Target Cookie name, Custom Session Cookies, Target Username(s), and Password Length.</li>
  <li><b>Manual Password Length:</b> User supplies the exact length via <code>-l</code> for maximum speed — no slow auto-detection overhead.</li>
  <li><b>Multi-Threaded Enumeration:</b> Parallel character extraction via <code>ThreadPoolExecutor</code> (configurable workers).</li>
  <li><b>Dual Detection Logic:</b> Boolean engine matches a configurable success string; Error engine detects server-side 500 errors reliably.</li>
  <li><b>Oracle & MySQL Payloads:</b> Uses <code>SUBSTR()</code> for Oracle-based labs and <code>substring()</code> for Boolean-based labs.</li>
  <li><b>Custom Charset:</b> Alphanumeric by default; enable <code>-s</code> flag to include special characters.</li>
  <li><b>Burp Suite Integration:</b> Built-in proxy support to route traffic through Burp Suite (<code>127.0.0.1:8080</code>) for debugging and monitoring requests.</li>
  <li><b>Browser-Like Headers:</b> Sends realistic User-Agent and browser headers to bypass basic WAF filtering.</li>
  <li><b>Auto Log Saving:</b> All extraction logs are saved to a dedicated <code>logs/</code> directory with timestamped filenames.</li>
  <li><b>Real-time Progress Tracker:</b> Displays live character extraction updates directly in your terminal.</li>
  <li><b>Multi-User Support:</b> Pass comma-separated usernames to extract passwords for multiple accounts in a single run.</li>
  <li><b>Cross-Platform Compatibility:</b> Works on Linux, Ubuntu, Kali Linux, macOS, Windows, and Android (via Termux).</li>
</ul>

<hr>

<h2>Folder Structure</h2>

<pre><code>Blind-SQLi-Brute-Tool/
├── main.py
├── readme.md
├── requirements.txt
├── tools/
│   ├── __init__.py
│   ├── common.py
│   ├── boolean_sqli.py
│   └── error_sqli.py
└── logs/
    └── (auto-generated log files)
</code></pre>

<hr>

<h2>Installation & Usage Guide</h2>

<p>Make sure you have <b>Python 3</b> and <b>pip</b> installed on your system before proceeding.</p>

<h3>Linux / Ubuntu / Kali Linux</h3>

<pre><code>git clone https://github.com/mdhaidarobs/Blind-SQLi-Brute-Tool.git
cd Blind-SQLi-Brute-Tool
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
chmod +x main.py
python3 main.py
</code></pre>

<hr>

<h3>macOS</h3>

<pre><code>git clone https://github.com/mdhaidarobs/Blind-SQLi-Brute-Tool.git
cd Blind-SQLi-Brute-Tool
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
python3 main.py
</code></pre>

<hr>

<h3>Windows (Command Prompt / PowerShell)</h3>

<ol>
  <li>Install Python from <a href="https://www.python.org/downloads/">python.org</a>.</li>
  <li>Make sure to check <b>Add Python to PATH</b> during installation.</li>
  <li>Open CMD or PowerShell and run:</li>
</ol>

<pre><code>git clone https://github.com/mdhaidarobs/Blind-SQLi-Brute-Tool.git
cd Blind-SQLi-Brute-Tool
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
</code></pre>

<hr>

<h3>Android (Termux)</h3>

<p>To set up the project on an Android device using Termux:</p>

<pre><code>pkg update && pkg upgrade
pkg install git python -y
git clone https://github.com/mdhaidarobs/Blind-SQLi-Brute-Tool.git
cd Blind-SQLi-Brute-Tool
pip install -r requirements.txt
python main.py
</code></pre>

<hr>

<h2>Usage Examples</h2>

<h3>Interactive Mode (Recommended)</h3>

<pre><code>python3 main.py
</code></pre>

<p>The tool displays a selector menu:</p>

<pre><code>[1] Boolean-based Blind SQLi  (response contains "Welcome back")
[2] Error-based Blind SQLi    (server returns HTTP 500 / Internal Server Error)
[3] Exit
</code></pre>

<p>Choose <code>1</code> or <code>2</code> and follow the interactive prompts.</p>

<h3>Direct CLI Mode</h3>

<p><b>Boolean-based lab:</b></p>

<pre><code>python3 main.py -m1 -u "https://LAB.web-security-academy.net/filter?category=Gifts" \
  -t "YOUR_TRACKING_ID" -sc "YOUR_SESSION_ID" -l 20 -w 1 -s
</code></pre>

<p><b>Error-based (Oracle) lab:</b></p>

<pre><code>python3 main.py -m2 -u "https://LAB.web-security-academy.net/filter?category=Gifts" \
  -t "YOUR_TRACKING_ID" -sc "YOUR_SESSION_ID" -l 20 -w 1 -s
</code></pre>

<hr>

<h2>Available Arguments</h2>

<table>
  <thead>
    <tr>
      <th>Flag</th>
      <th>Description</th>
      <th>Required</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>-u</code> / <code>--url</code></td>
      <td>Target lab URL (base endpoint or <code>/filter?category=...</code>)</td>
      <td>Yes</td>
    </tr>
    <tr>
      <td><code>-t</code> / <code>--tracking</code></td>
      <td>Base TrackingId value (without trailing <code>' --</code>)</td>
      <td>Yes</td>
    </tr>
    <tr>
      <td><code>-sc</code> / <code>--session</code></td>
      <td>Session cookie value (for PortSwigger labs)</td>
      <td>Optional</td>
    </tr>
    <tr>
      <td><code>-c</code> / <code>--cookie</code></td>
      <td>Vulnerable cookie name (default: <code>TrackingId</code>)</td>
      <td>Optional</td>
    </tr>
    <tr>
      <td><code>-usr</code> / <code>--users</code></td>
      <td>Comma-separated usernames (default: <code>administrator</code>)</td>
      <td>Optional</td>
    </tr>
    <tr>
      <td><code>-l</code> / <code>--length</code></td>
      <td>Password length (mandatory — must be a positive integer)</td>
      <td>Yes</td>
    </tr>
    <tr>
      <td><code>-w</code> / <code>--workers</code></td>
      <td>Parallel worker threads (use <code>1</code> for PortSwigger)</td>
      <td>Optional</td>
    </tr>
    <tr>
      <td><code>-T</code> / <code>--timeout</code></td>
      <td>Request timeout in seconds (default: 15)</td>
      <td>Optional</td>
    </tr>
    <tr>
      <td><code>-p</code> / <code>--proxy</code></td>
      <td>Proxy URL (e.g., <code>http://127.0.0.1:8080</code>)</td>
      <td>Optional</td>
    </tr>
    <tr>
      <td><code>-s</code> / <code>--special</code></td>
      <td>Include special characters in the charset</td>
      <td>Optional</td>
    </tr>
    <tr>
      <td><code>-o</code> / <code>--log</code></td>
      <td>Custom log filepath (default: <code>logs/*_YYYYMMDD_HHMMSS.log</code>)</td>
      <td>Optional</td>
    </tr>
  </tbody>
</table>

<hr>

<h2>PortSwigger Lab Tips</h2>

<ul>
  <li>Copy a <b>fresh</b> <code>TrackingId</code> and <code>session</code> cookie from your browser before every run.</li>
  <li>Always set <code>-w 1</code> (single worker) to avoid rate-limiting on PortSwigger servers.</li>
  <li>Ensure the URL ends with <code>/filter?category=...</code> — do not use <code>/login</code>.</li>
  <li>Sessions expire roughly in ~10 minutes, so run the tool immediately after copying cookies.</li>
  <li>For Boolean-based labs, the success string is <code>"Welcome back"</code>. For custom targets, override it with <code>--success-indicator</code>.</li>
  <li>For Oracle-based error labs, the payload uses <code>SUBSTR()</code> and <code>TO_CHAR(1/0)</code> — the server returns HTTP 500 when the condition is TRUE.</li>
</ul>

<hr>

<h2>Logs</h2>

<p>Every run automatically writes a timestamped log file under the <code>logs/</code> folder:</p>

<pre><code>logs/boolean_sqli_20260104_153034.log
logs/error_sqli_20260104_154522.log
</code></pre>

<p>Each log records every character position found, aiding post-run analysis and debugging.</p>

<hr>

<h2>Requirements</h2>

<pre><code>requests>=2.31.0
urllib3>=2.0.0
colorama>=0.4.6
</code></pre>

<p>Install all at once with:</p>

<pre><code>pip install -r requirements.txt
</code></pre>

<hr>

<p><b>Note:</b> Use only in intentionally vulnerable labs or systems where you have explicit authorization.</p>

<hr>

<h2>Creator & Connect</h2>

<ul>
  <li><b>Creator:</b> Md Haidar</li>
  <li><b>GitHub:</b> <a href="https://github.com/mdhaidarobs">@mdhaidarobs</a></li>
  <li><b>LinkedIn:</b> <a href="https://www.linkedin.com/in/haidarobs">haidarobs</a></li>
</ul>

<hr>

<h2>Disclaimer</h2>

<p><i>This tool is created strictly for educational purposes, ethical hacking, and practicing on authorized security labs (such as PortSwigger Web Security Academy). Do not use this tool against unauthorized systems or targets without explicit permission. The creator is not responsible for any misuse or damage caused by this tool.</i></p>