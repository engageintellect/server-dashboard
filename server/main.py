#!/usr/bin/env python3

from fastapi import FastAPI, WebSocket
import subprocess
import uvicorn
import asyncio

app = FastAPI()


@app.get("/api/hostname")
def get_hostname():
    return subprocess.getoutput("cat /etc/hostname")


@app.get("/api/os")
def get_os():
    return subprocess.getoutput("cat /etc/os-release | grep PRETTY_NAME | cut -d '=' -f2 | tr -d '\"'")


@app.get("/api/uptime")
def get_uptime():
    return subprocess.getoutput("uptime -p | sed 's/up //'")

# @app.get("/api/memory/used")
# def get_used_ram():
#     return subprocess.getoutput("free | awk '/Mem:/ { printf(\"%.2f%%\\n\", $3/$2 * 100) }'")


@app.get("/api/memory/used")
def get_used_ram():
    return subprocess.getoutput("free | awk '/Mem:/ { printf(\"%.2f%%\\n\", $3/$2 * 100) }'")


@app.get("/api/memory/available")
def get_available_ram():
    return subprocess.getoutput('free | awk \'/Mem:/ { printf("%.2f GB\\n", $7/1048576) }\'')

# @app.get("/api/memory/available")
# def get_available_ram():
#     return subprocess.getoutput("free | awk '/Mem:/ { printf(\"%.2f\\n\", $7/$2 * 100) }'")


@app.get("/api/cpu/usage")
def get_cpu_usage():
    return subprocess.getoutput("mpstat 1 1 | awk '/Average:/ && $12 ~ /[0-9.]+/ { printf(\"%.2f%%\\n\", 100 - $12) }'")


@app.get("/api/disk/usage")
def get_disk_usage():
    return subprocess.getoutput("df / | awk 'NR==2 { printf(\"%.2f%%\\n\", $5) }'")


@app.get("/api/updates")
def get_network_usage(interface="eth0"):
    command = f"sudo apt update > /dev/null 2>&1 && apt list --upgradable 2>/dev/null | grep -v Listing | wc -l"
    return subprocess.getoutput(command)


@app.get("/api/network/usage")
def get_network_usage(interface="eth0"):
    command = f"sar -n DEV 1 1 | awk '/Average: {
        interface}/ {{ printf(\"RX: %.2f KB/s, TX: %.2f KB/s\\n\", $5, $6) }}'"
    return subprocess.getoutput(command)


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


@app.websocket("/api/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = {
            "hostname": get_hostname(),
            "os": get_os(),
            "uptime": get_uptime(),
            "memoryUsed": get_used_ram(),
            "memoryAvailable": get_available_ram(),
            "cpuUsage": get_cpu_usage(),
            "diskUsage": get_disk_usage(),
            "networkUsage": get_network_usage(),
            "networkLatency": get_network_latency(),
            "networkPorts": get_open_ports(),
            "runningServices": get_running_services(),
        }
        await websocket.send_json(data)
        await asyncio.sleep(3)  # Send updated data every 5 seconds

if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=6767)
