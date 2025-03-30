# AdWard
A subscription-based application for a variety of platforms that serves the purpose of intercepting and blocking ads at the network level. Users will pay a monthly subscription for the privilege of blocking ads for websites, social media apps, and games on a device of your choosing.  

## Intent 
The following contract was written and agreed upon by William Mayer, Iaan Wheeler, Jason Spears & Venkateswaran Naresh. The contract provides expectations, objectives, and results for developing the AdWard.
The contract is effective for all team members participating in the Senior Design Capstone class series in the 2024-2025 academic year.

## Problem Statement
Ads and monetization have run rampant across websites and applications with invasive ads that impede the use of unintrusive browsing sites, social media, and games. We seek to provide a device solution for such problems. With the use of the AdWard plugin or app on your computer or phone you can actively block the addresses associated (Avoidthehack!, 2023) with video and banner ads such that they do not display.

## Solution
There is existing technology in place in which you can create DNS sinkholes for certain IPs related ads displayed within websites and apps. The method by which you can create an ad blocker over network traffic is to check for certain calls from the website itself and if the IP for the ad is in the database of the application, that advertisement traffic is blocked from the website and thus adds are not displayed.

# Project Goals
The goal of this project is to create software as a service (SaaS) subscription-based program allowing users to receive filtered internet traffic avoiding advertisements. 

- Filter incoming DNS traffic 
- Not log user data through filter 
- Ability to select varying levels of traffic filtering
- Allowlist/Blocklist for additional user control

## Project Scope
The goal is a one-click solution (like existing VPN technology), that will route traffic to our servers to cross-reference with our block listing (Avoidthehack!, 2023) before routing the traffic back to the enabled device, eliminating unnecessary traffic in the process. This will hopefully be implemented at an acceptable speed at parity with unfiltered traffic. To differentiate this from the self-hosted open-source implementation, we will be monetized monthly/yearly for a subscription service that can be configured in a wide variety of fashions, with varying models of severity of traffic filtering, such as anti-NSFW filters for family devices.

## Technolgoies Used
- Dnsmasq 
- Curl 
- FTL
- Python
- Bash
- Lighttpd
- ADMinLTE Dash
- Sqlite3
- ChatGPT
- Scapy 

## Collaborators
- Jason Spears 
- William Mayer
- Venkateswaran Naresh
- Iaan Wheeler

## Setup and Upkeep

start a virtual environment to manage the dependencies with 
```
python -m venv venv
```
The activate the environment based on your system
Mac/Linux
```
source venv/bin/activate
```
Windows 
```
venv\Scripts\activate
```
Install the requirements.txt with the following command 
```
pip install -r requirements.txt
```


## building the app 
 
Please note this is for the GUI in vscode/vscodium if other adapt instructions

Install the neccesary extensions 
- Python
- Python debugger

Go to sidebar and there should be the 'Run & Debug' section and click the start button. The dropdown should read "Adward Qt App, if not, select that and then run.

his should result in a new window for the app if it does not work while in the 'main' branch, contact maintainer.
