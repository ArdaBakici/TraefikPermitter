from datetime import datetime
from flask import Flask, redirect, render_template, url_for, request, session
import json
import time
import yaml
import threading

#2024091505561244620
lock = threading.Lock()
app = Flask(__name__)
default_timeout = 18000 # in seconds
whitelist_file = 'lists/whitelist.json'
traefik_config = 'lists/mc-java.yml'
race_condition = False

def check_if_allowed(ip):
    allowed_ips = None
    with lock:
        with open(whitelist_file, 'r') as file:
            allowed_ips = json.load(file)
    if ip in allowed_ips:
        return allowed_ips[ip]
    else:
        return -1

def update_traefik():
    while True:
        traefik_list = None
        allowed_ips = None
        final_ip_list = {}
        with lock:
            with open(whitelist_file, 'r') as file:
                allowed_ips = json.load(file)
            for ip in allowed_ips:
                if allowed_ips[ip] > int(datetime.timestamp(datetime.now())):
                    final_ip_list[ip] = allowed_ips[ip] 
            with open(whitelist_file, 'w') as file:
                json.dump(final_ip_list, file, indent=4)
        with open(traefik_config, 'r') as file:
            traefik_list = yaml.safe_load(file)
        traefik_list['tcp']['middlewares']['mc-ipallowlist']['ipAllowList']['sourceRange'] = []
        for ip in final_ip_list:
            traefik_list['tcp']['middlewares']['mc-ipallowlist']['ipAllowList']['sourceRange'].append(f'{ip}/32') 
        with open(traefik_config, 'w') as file:
            yaml.dump(traefik_list, file)
        time.sleep(5)

def write_ip(ip):
    with lock:
        allowed_ips = {}
        with open(whitelist_file, 'r') as file:
            allowed_ips = json.load(file)

        allowed_ips[ip] = int(datetime.timestamp(datetime.now()) + default_timeout)

        with open(whitelist_file, 'w') as file:
            json.dump(allowed_ips, file, indent=4)


@app.route('/permit', methods=['GET'])
def permit():
    client_ip = request.remote_addr
    write_ip(client_ip)
    return redirect(url_for('home'))

@app.route('/', methods=['GET'])
def home():
    client_ip = request.remote_addr
    print(client_ip)
    time_allowed = check_if_allowed(client_ip)
    if(time_allowed < int(datetime.timestamp(datetime.now()))):
        return render_template('not_allowed.html')
    else:
        return render_template('allowed.html', countdown=time_allowed)

thread = threading.Thread(target=update_traefik)
thread.start()
