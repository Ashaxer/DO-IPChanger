# Introducing project
DigitalOcean Float IP Checker &amp; Changer + TelegramBOT

This project is used to automatically change the float IP of your DigitalOcean droplets whenever it gets blocked by IR@N GFW.


| Feature  | Supported |
|-----|:-----:|
| Auto checks &amp; changes all float IPs  |  ✅  |
| Auto sets each droplet IP to desired subdomain  |  ✅  |
| Runing TelegramBot for managing IPs  |  ✅  |
| Flexible result checking precentage  |  ✅  |

# How it works
The bot gathers the list of droplets it has to check from the .env file and then checks their float IP address assigned to them.

Using check-host.net, it checks if the IP is blocked in IR@N.

The bot starts a loop where it changes the float IP of that droplet and checks it until the IP is clean.

Then using your CloudFlare account, it assigns the IP to your desired sub domain.


You can Check or Change your droplets Float IPs using TelegramBot too.

# Collecting the Configuration Info
## DigitalOcean
Login to your DigitalOcean Panel, Assign float IP to your droplets and gather your droplet hostnames. #Example: ubuntu-s-4vcpu-8gb-amd-fra1
Generate API Key and save it somewhere.

## CloudFlare
Login to your CloudFlare Panel, Inside your profile, save your API Global Key.

Select your desired domain, In Dashboard menu, from the right panel, save your zone_id.

Create a new Origin Certificate from SSL/TLS menu and save the Public Key and Private Key files.

Set a subdomain to your server running the BOT. (Enable the Proxy)


## Telegram
Create a Telegram Bot using [BotFather](https://telegram.me/BotFather) and save your Bot Token.

Copy a Telegram Channel ID or Group ID for logging purposes.

Copy your Telegram UserID for Managing the Bot. (you can use [This Bot](https://telegram.me/usinfobot))


# Configuring

Clone the project into your server.

edit the .env file and add your previous gathered information like this:

```env
cf_email = "" #Your CloudFlare Email Address
cf_api_key = "" #Your CloudFlare API Global Key
cf_zone_id = "" #Your CloudFlare Domain ZoneID
cf_domain = "" #Your CloudFlare Domain Name
cf_subdomain = "" #The Subdomain for setting the new float IP Example: clean
domain_cheatsheet = {} # Example: {"ubuntu-s-4vcpu-8gb-amd-fra1":"frankfurt1", "ubuntu-s-24vcpu-4gb-amd-fra1":"frankfurt2", "ubuntu-s-4vcpu-8gb-amd-ams1":"amsterdam"}
#In this example, droplet "ubuntu-s-4vcpu-8gb-amd-fra1" IP will be checked and
#if renew was necessarry, new IP will set to clean.frankfurt1.shaxerver.online
do_api_key = "" #Your DigitalOcean API Key
do_base_url = "" #DigitalOcean API BaseURL, It's default
bot_token = "" #TelegramBot Token for sending logs
chat_id = "" #Telegram GroupID or ChannelID for sending logs.
proxy = "" #Proxy if needed to connect servers Example: 'socks5h://localhost:40000'
acceptable_connectivity = "" #Minimum precentage check-host.net result, set 0 to use default or use minus percent to use minus default percent #Exampel -15 means (Maximum result of 8.8.8.8 check - 15)
wh_bot_token = "" #TelegramBot Token for managing the IPs
wh_bot_admins = [] #Telegram UserIDs as admins
wh_ip_address = "" #webhook IP Address, Default empty for secure connection
wh_url = "" #webhook domain:<HTTPS PORT>
wh_secret_token = "" #webhook secret token
wh_cert = "" #CloudFlare Origin public key file path
wh_key = "" #CloudFlare Origin private key file path
```

# Scheduling and Running the bots
Before doing anything, lets setup a virtual enviroment inside your project folder (make sure you are inside DO-IPChanger folder):  
If coming from Ubuntu 24+ and you haven't added ```deadsnakes``` repo yet, run these:
```
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
```
Then
```
sudo apt install python3.11 python3.11-venv python3.11-dev
```
Clone this repo and navigate to it
```
git clone https://github.com/Ashaxer/DO-IPChanger.git
cd DO-IPChanger
python3.11 -m venv venv #if you want to use your custom venv name, you also need to manually update the cronjobs
```

To use the bot files, activate the venv and then install requirements:
```
source venv/bin/activate
pip install -r requirements.txt
```

You can also install webhooks requirements using this command:
```
source venv/bin/activate
pip install -r aiogram<3
```


You can use ```bash install.sh``` to install cronjobs for Webhooks or Checker.

Don't forget to activate venv before running scripts!
```
source venv/bin/activate
```

## TelegramBot IP Manager
For running the Webhook Bot, run the webhook.py file using python3.11
```
python3.11 -m webhook.py
```

## Auto Checker and Logger
For running a single check operation, run the check.py file using python3.11
```
python3.11 -m check.py
```

