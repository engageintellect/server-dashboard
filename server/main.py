#!/usr/bin/env python3
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, HTTPException
import subprocess
import uvicorn
import asyncio
import os

load_dotenv()

app = FastAPI()

package_manager = os.getenv("PACKAGE_MANAGER")


@app.get("/api/hostname")
def get_hostname():
    return subprocess.getoutput("cat /etc/hostname")


@app.get("/api/os")
def get_os():
    return subprocess.getoutput("cat /etc/os-release | grep PRETTY_NAME | cut -d '=' -f2 | tr -d '\"'")


@app.get("/api/uptime")
def get_uptime():
    return subprocess.getoutput("uptime -p | sed 's/up //'").split(',')


@app.get("/api/temp")
def get_temp():
    output = subprocess.getoutput(
        "cat /sys/class/thermal/thermal_zone0/temp | awk '{printf \"%.2f°F\\n\", $1/1000 * 9/5 + 32}'")
    return output.strip()


@app.get("/api/memory/used")
def get_used_ram():
    return subprocess.getoutput("free | awk '/Mem:/ { printf(\"%.2f\\n\", $3/$2 * 100) }'")


@app.get("/api/memory/available")
def get_available_ram():
    return subprocess.getoutput('free | awk \'/Mem:/ { printf("%.2f\\n", $7/1048576) }\'')


@app.get("/api/cpu/usage")
def get_cpu_usage():
    return subprocess.getoutput("mpstat 1 1 | awk '/Average:/ && $12 ~ /[0-9.]+/ { printf(\"%.2f\\n\", 100 - $12) }'")


@app.get("/api/disk/usage")
def get_disk_usage():
    return subprocess.getoutput("df / | awk 'NR==2 { printf(\"%.2f\\n\", $5) }'")


@app.get("/api/load")
def get_load():
    with open('/proc/loadavg', 'r') as file:
        load_data = file.readline().split()

    min1, min5, min15 = load_data[:3]
    cpucore = os.cpu_count()

    load_dict = {
        "min1": float(min1),
        "min5": float(min5),
        "min15": float(min15),
        "cpucore": cpucore
    }

    return load_dict


@app.get("/api/package-count")
def get_package_count():
    command = "neofetch | grep Packages | awk '{print $2}'"
    return subprocess.getoutput(command)


@app.get("/api/updates")
def get_updates():
    if package_manager == "apt":
        command = f"sudo apt update > /dev/null 2>&1 && apt list --upgradable 2>/dev/null | grep -v Listing | wc -l"

    if package_manager == "pacman":
        command = f"sudo sh -c 'pacman -Syq --noconfirm > /dev/null 2>&1 && pacman -Quq 2> /dev/null | wc -l'"
    return subprocess.getoutput(command)


@app.get("/api/updatable-packages")
def get_updatable_packages():
    command = 'sudo apt list --upgradable 2>/dev/null'
    output = subprocess.getoutput(command)
    upgradable_packages = [line for line in output.split(
        '\n') if 'upgradable from' in line]
    package_list = [line.split()[0] for line in upgradable_packages]
    return package_list


@app.get("/api/network/usage")
def get_network_usage(interface="lo"):
    received_command = f"ifconfig {interface} | grep 'RX packets' | awk '{{printf \"%.2f\\n\", $5/1024/1024}}'"
    sent_command = f"ifconfig {interface} | grep 'TX packets' | awk '{{printf \"%.2f\\n\", $5/1024/1024}}'"
    received = subprocess.getoutput(received_command)
    sent = subprocess.getoutput(sent_command)
    return {"received": received, "sent": sent}


@app.get("/api/network/latency")
def get_network_latency(host="google.com"):
    command = f"ping -c 4 {host} | tail -1| awk -F '/' '{{print $5 \" ms\"}}'"
    return subprocess.getoutput(command)


@app.get("/api/network/ports")
def get_open_ports():
    command = "nmap -sT localhost | awk '/^[0-9]+\\/tcp/ {print $1}'"
    output = subprocess.getoutput(command)
    ports = [int(port.split("/")[0]) for port in output.split('\n') if port]
    return ports


@app.get("/api/services/running")
def get_running_services():
    command = "systemctl list-units --type=service --state=running | grep '\.service' | awk '{print $1}'"
    output = subprocess.getoutput(command)
    services = output.split('\n')
    return services

# @app.get("/api/processes")
# def get_running_processes():
#     processes = requests.get(f'{GLANCES_ENDPOINT}/processlist')
#     return processes.json()


@app.get("/api/processes")
def get_running_processes():
    command = "ps aux --sort=-%mem | head -n 21"
    try:
        result = subprocess.run(
            command, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if result.stderr:
            print("Error:", result.stderr)
            raise HTTPException(status_code=500, detail=result.stderr)

        lines = result.stdout.splitlines()
        processes = []
        for line in lines[1:]:  # Skip the header line
            parts = line.split(maxsplit=10)
            if len(parts) >= 11:
                process = {
                    "user": parts[0],
                    "pid": parts[1],
                    "cpu": parts[2],
                    "mem": parts[3],
                    # Assumes the command may include spaces beyond part[10]
                    "command": parts[10]
                }
                processes.append(process)

        return processes

    except subprocess.CalledProcessError as e:
        print("Command failed:", e)
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        print("Unexpected error:", str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/api/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print(f"WebSocket connection established with: {websocket.client}")
    try:
        while True:
            data = {
                "hostname": get_hostname(),
                "os": get_os(),
                "uptime": get_uptime(),
                "temp": get_temp(),
                "memoryUsed": get_used_ram(),
                "memoryAvailable": get_available_ram(),
                "cpuUsage": get_cpu_usage(),
                "diskUsage": get_disk_usage(),
                "systemLoad": get_load(),
                "packageCount": get_package_count(),
                "updates": get_updates(),
                # "updatablePackages": get_updatable_packages(),
                "networkUsage": get_network_usage(),
                "networkLatency": get_network_latency(),
                "networkPorts": get_open_ports(),
                "runningServices": get_running_services(),
                "systemProcesses": get_running_processes(),
            }
            await websocket.send_json(data)
            await asyncio.sleep(5)  # Send updated data every 5 seconds
    except Exception as e:
        print(f"WebSocket connection error: {e}")
    finally:
        print(f"WebSocket connection closed with: {websocket.client}")

if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=4320)
    # uvicorn.run("main:app", host="0.0.0.0", port=4321, ssl_keyfile="/etc/letsencrypt/live/engage-dev.com/privkey.pem",
    #            ssl_certfile="/etc/letsencrypt/live/engage-dev.com/fullchain.pem")
