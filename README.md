# Blind-SQLi-Brute-Tool
A command-line tool to automate Blind SQL Injection vulnerability exploitation

 <h1> Blind SQL Injection Automation Tool (CLI)</h1>

<p>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.x-blue.svg" alt="Python Version"></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="MIT License"></a>
  <a href="https://github.com/mdhaidarobs"><img src="https://img.shields.io/badge/Author-Md%20Haidar-orange.svg" alt="Author"></a>
</p>

<p>
A lightweight, powerful, and interactive Command-Line Interface (CLI) tool designed to automate <b>Blind SQL Injection (Conditional Responses)</b> testing. Built for security enthusiasts, penetration testers, and CTF players to practice database security testing in authorized environments.
</p>

<hr>

<h2>Tool Screenshots</h2>

<p><i>Here is a quick preview of the tool in action:</i></p>

<h3>1. Interactive Configuration & Setup</h3>

<img src="docs/images/config-preview.png" alt="Tool Configuration Screenshot" width="100%">

<p><i>User providing URL, Tracking ID, Cookie name, and Target User.</i></p>

<h3>2. Live Enumeration Output</h3>

<img src="docs/images/brute-preview.png" alt="Tool Running Screenshot" width="100%">

<p><i>Real-time character-by-character enumeration in Linux Terminal.</i></p>

<hr>

<h2> Features & Benefits</h2>

<ul>
  <li><b>Interactive CLI Wizard:</b> Full user control over URL, Target Cookie name, Custom Session Cookies, Target Username, and Password Length.</li>
  <li><b>Burp Suite Integration:</b> Built-in proxy support to route traffic through Burp Suite (<code>127.0.0.1:8080</code>) for debugging and monitoring requests.</li>
  <li><b>Fast Enumeration:</b> Uses Python <code>requests</code> for efficient HTTP communication in authorized testing environments.</li>
  <li><b>Cross-Platform Compatibility:</b> Works on Linux, Ubuntu, Kali Linux, macOS, Windows, and Android (via Termux).</li>
  <li><b>Real-time Progress Tracker:</b> Displays live character extraction updates directly in your terminal.</li>
</ul>

<hr>

<h2>Installation & Usage Guide</h2>

<p>Make sure you have <b>Python 3</b> and <b>pip</b> installed on your system before proceeding.</p>

<h3>Linux / Ubuntu / Kali Linux</h3>

<pre><code>git clone https://github.com/mdhaidarobs/Blind-SQLi-Brute-Tool.git
cd Blind-SQLi-Brute-Tool
pip install requests
chmod +x sqli_tool.py
python3 sqli_tool.py</code></pre>

<p><b>Optional:</b> To make the script available as a system-wide command:</p>

<pre><code>sudo cp sqli_tool.py /usr/local/bin/sqli-tool
sqli-tool</code></pre>

<hr>

<h3>macOS</h3>

<pre><code>git clone https://github.com/mdhaidarobs/Blind-SQLi-Brute-Tool.git
cd Blind-SQLi-Brute-Tool
pip3 install requests
python3 sqli_tool.py</code></pre>

<hr>

<h3>Windows (Command Prompt / PowerShell)</h3>

<ol>
  <li>Install Python from <a href="https://www.python.org/downloads/">python.org</a>.</li>
  <li>Make sure to check <b>Add Python to PATH</b> during installation.</li>
  <li>Open CMD or PowerShell and run:</li>
</ol>

<pre><code>git clone https://github.com/mdhaidarobs/Blind-SQLi-Brute-Tool.git
cd Blind-SQLi-Brute-Tool
pip install requests
python sqli_tool.py</code></pre>

<hr>

<h3>📱 Android (Termux)</h3>

<p>To set up the project on an Android device using Termux:</p>

<pre><code>pkg update && pkg upgrade
pkg install git python -y

git clone https://github.com/mdhaidarobs/Blind-SQLi-Brute-Tool.git
cd Blind-SQLi-Brute-Tool

pip install requests
python sqli_tool.py</code></pre>

<hr>

<h2>How to Use</h2>

<ol>
  <li>Run the script using Python.</li>
  <li>Enter your authorized testing lab URL.</li>
  <li>Provide the required session and tracking information.</li>
  <li>Configure the target cookie and testing parameters.</li>
  <li>Enter the target username and expected password length.</li>
  <li>Configure Burp Suite proxy if required.</li>
  <li>Monitor the testing progress in your terminal.</li>
</ol>

<p><b>Note:</b> Use only in intentionally vulnerable labs or systems where you have explicit authorization.</p>

<hr>

<h2>Creator & Connect</h2>

<ul>
  <li><b>Creator:</b> Md Haidar</li>
  <li><b>GitHub:</b> <a href="https://github.com/mdhaidarobs">@mdhaidarobs</a></li>
</ul>

<hr>

<h2>Disclaimer</h2>

<p>
<i>
This tool is created strictly for educational purposes, ethical hacking, and practicing on authorized security labs (such as PortSwigger Web Security Academy). Do not use this tool against unauthorized systems or targets without explicit permission. The creator is not responsible for any misuse or damage caused by this tool.
</i>
</p>
