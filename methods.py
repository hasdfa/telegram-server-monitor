from subprocess import check_output
import requests
import datetime
import psutil
import config
import persistence
import time
import traceback
import os
import re

last_notification = 0
storage = persistence.UsersDatabase()

def processCommand(chat_id, cmd):
    print("[{0}] >>> {1}\n".format(chat_id, cmd))
    stdout = ""
    try:
        stdout = check_output(cmd, shell=True)
        stdout = stdout.decode("utf-8")
        print("[{0}] <<< {1}\n".format(chat_id, stdout))
    except Exception as err:
        print("Error received: {}\n".format(err))
        stdout = "{0}".format(err)
    sendTextMessage(chat_id, "$ {0}\n".format(stdout))

def processSystemctlCommand(chat_id, ctl_action, service_name):
    processCommand(chat_id, "systemctl -l -q {0} {1}\n".format(ctl_action, service_name))

def changeHealthcheckStatus(chat_id, status):
    myfile = open(os.getenv("BACKEND_HEALTH_FILE", "/BackendHealth"), 'w')
    myfile.write(status)
    myfile.close()
    sendTextMessage(chat_id, "[BACKEND-HEALTH]: " + status)

def processMessage(message):
    if "text" in message:
        processTextMessage(message)
    else:
        raise Exception("Unsupported message type")

def processTextMessage(message):
    text = message["text"]

    if text.startswith("/"):
        processCommandMessage(message)
     else:
        raise Exception("Plain text is not supported")

def processCommandMessage(message):
    chat_id = message["chat"]["id"]
    text = message["text"]
    
    def unsupportedCommand(overwrite="{0} - unsupported command"):
        sendTextMessage(chat_id, overwrite.format(text))

    if " " in text:
        command, parameter = text.split(" ", 1)
    else:
        command = text
        parameter = ""

    if "@" in command:
        command, botname = command.split("@", 1)
        if botname.lower() != config.NAME.lower():
            # Ignore messages for other bots
            unsupportedCommand()
            return

    if command == "/start":
        commandStart(message, parameter)
    elif command == "/stop":
        commandStop(message)
    elif command == "/help":
        commandHelp(message)
    elif command == "/usage":
        commandUsage(message)
    elif command == "/users":
        commandUsers(message)
    elif command == "/disks":
        commandDisks(message)
    elif command == "/shell":
        processCommand(chat_id, parameter)
    elif command == "/service":
        if " " in text:
            ctl_action, service_name = parameter.split(" ", 1)
        else:
            ctl_action = parameter
            service_name = config.SYSTEMCTL_DEFAULT_SERVICE_NAME
        if ctl_action not in ["start", "status", "stop", "reload", "restart", "kill"]:
            unsupportedCommand()
            return
        processSystemctlCommand(chat_id, ctl_action, service_name)
    elif command == "/health":
        if parameter not in ["alive", "dead"]:
            unsupportedCommand()
            return
        changeHealthcheckStatus(chat_id, parameter)
    else:
        unsupportedCommand()

def sendTextMessage(chat_id, text):
    try:
        r = requests.post(config.API_URL + "sendMessage", json={
            "chat_id" : chat_id,
            "text" : text
        })
        print(r.json())
    except Exception as err:
        print("Send error: {0}\n".format(err))

def sendAuthMessage(chat_id):
    sendTextMessage(chat_id, "Please sign in first.")

def startupMessage():
    for id in storage.allUsers():
        sendTextMessage(id, "Hello there. I just started.")

def shutdownMessage():
    for id in storage.allUsers():
        sendTextMessage(id, "I am shutting down.")

def commandStart(message, parameter):
    chat_id = message["chat"]["id"]
    if storage.isRegisteredUser(chat_id):
        sendTextMessage(chat_id, "You are signed in. Thank you.")
    else:
        if parameter.strip() == config.PASSWORD:
            storage.registerUser(chat_id)
            sendTextMessage(chat_id, "Thanks for signing up. " +
                "Type /help for information.")
        else:
            sendTextMessage(chat_id, "Please provide a valid password. " +
                "Type /start <password> to sign in.")

def commandStop(message):
    chat_id = message["chat"]["id"]
    if storage.isRegisteredUser(chat_id):
        storage.unregisterUser(chat_id)
        sendTextMessage(chat_id, "You signed off. You will no longer receive any messages from me.")
    else:
        sendAuthMessage(chat_id)

def commandHelp(message):
    chat_id = message["chat"]["id"]
    sendTextMessage(chat_id, config.NAME + """
Monitor your server and query usage and network information.
/usage - CPU and Memory information
/users - Active users
/disks - Disk usage

Shell
/shell $command - Execute ssh command

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
""")

def commandUsage(message):
    chat_id = message["chat"]["id"]
    if not storage.isRegisteredUser(chat_id):
        sendAuthMessage(chat_id)
        return
    
    virtual_memory = psutil.virtual_memory()

    text = """Uptime: {0}
CPU: {1}%
RAM: {2}% ({3}Mb of {4}Mb)
Swap: {5}%""".format(
    str(datetime.datetime.now() - datetime.datetime.fromtimestamp(psutil.boot_time())),
    psutil.cpu_percent(),
    virtual_memory.percent,
    "%.2f" % ((virtual_memory.total - virtual_memory.available) / (1024 * 1024)),
    "%.2f" % (virtual_memory.total / (1024 * 1024)),
    psutil.swap_memory().percent)
    sendTextMessage(chat_id, text)

def commandUsers(message):
    chat_id = message["chat"]["id"]
    if not storage.isRegisteredUser(chat_id):
        sendAuthMessage(chat_id)
        return

    text = ""
    for user in psutil.users():
        text = text + "{0}@{1} {2}\n".format(user.name, user.host, str(datetime.datetime.fromtimestamp(user.started)))
    if text == "":
        text = "No such users logged in\n"

    sendTextMessage(chat_id, text)

def commandDisks(message):
    chat_id = message["chat"]["id"]
    if not storage.isRegisteredUser(chat_id):
        sendAuthMessage(chat_id)
        return

    disk_usage = psutil.disk_usage('/')
    text = "Used {0}Gb of {1}Gb (free {2}Gb):\n\n".format(
        "%.2f" % (disk_usage.used / (1024 * 1024 * 1024)),
        "%.2f" % (disk_usage.total / (1024 * 1024 * 1024)),
        "%.2f" % (disk_usage.free / (1024 * 1024 * 1024))
    )

    for dev in psutil.disk_partitions():
        text = text + "{0} ({1}) {2} %\n".format(dev.device, dev.mountpoint, psutil.disk_usage(dev.mountpoint).percent)

    sendTextMessage(chat_id, text)

def alarms():
    global last_notification
    now = time.time()

    if config.ENABLE_NOTIFICATIONS and (now - last_notification > config.NOTIFCATION_INTERVAL):
        text = "Alarm!\n"
        should_send = False

        cpu = psutil.cpu_percent()
        virtual_memory = psutil.virtual_memory()
        
        ram = virtual_memory.percent
        ram_used = "%.2f" % ((virtual_memory.total - virtual_memory.available) / (1024 * 1024))
        ram_total = "%.2f" % (virtual_memory.total / (1024 * 1024))
        
        disk_usage = psutil.disk_usage('/')
        storage_percent = disk_usage.used / disk_usage.total
        
        if cpu > config.NOTIFY_CPU_PERCENT:
            text = text + "CPU: {0}%\n".format(cpu)
            should_send = True
        if ram > config.NOTIFY_RAM_PERCENT:
            text = text + "RAM: {0}% ({1}Mb of {2}Mb)\n".format(ram, ram_used, ram_total)
            should_send = True
        if storage_percent > config.NOTIFY_STORAGE_PERCENT:
            text = text + "Storage space: {0}% ({1}Gb of {2}Gb)\n".format(
                "%.2f" % storage_percent,
                "%.2f" % (disk_usage.used / (1024 * 1024 * 1024)),
                "%.2f" % (disk_usage.total / (1024 * 1024 * 1024)),
            )
            should_send = True

        if should_send:
            last_notification = now
            for id in storage.allUsers():
                sendTextMessage(id, text)

def commandShell(message, parameter):
    parameter.strip()
