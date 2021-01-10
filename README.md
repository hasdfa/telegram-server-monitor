# Telegram Server Monitor

Monitoring service writen in Python3 to be hosted on your own server.

## Commands
```
Monitor your server and query usage and network information.
/usage - CPU and Memory information
/users - Active users
/disks - Disk usage

Shell
/shell $command - Execute shell command

Systemctl service manage
/service start $name - Start service
/service status $name - Status of service
/service restart $name - Restart service
/service kill $name - Send signal to processes of a unit
/service stop $name - Stop service

Backend healthcheck
/health alive - Set healthcheck to alive
/healt dead - Set healthcheck to dead

You do not like me anymore?
/stop - Sign off from the monitoring service
```

## Installation
**Talk to @BotFather on Telegram**
- Type `/start` to start a conversation with the bot father.
- Type `/newbot` and follow the instructions to create our own bot.
- Remember the access token - you will need it later.
- You may configure your bot by setting a name or picture.

**Configure your linux server**

```sh
# Create a special user for the bot
sudo adduser telegram --gecos "" --disabled-password

# Install Python 3 and its package manager
sudo apt-get install python3 python3-pip

# Install Python Requests and PSUtil Library
sudo python3 -m pip install requests psutil --upgrade
```

**Download and install Telegram Server Monitor**

```sh
# Change to the created user
su telegram
cd ~

git clone https://github.com/hasdfa/telegram-server-monitor.git
cd telegram-server-monitor
cp config.template.py config.py

# Edit the config file with your favorite editor
nano config.py
```
