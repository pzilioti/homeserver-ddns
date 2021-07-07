import configparser
import requests
import time
import logging
import os


def run():
    base_path = '/home/paolo/projects/homeserver-ddns/'

    config = configparser.ConfigParser()
    config.read(os.path.join(base_path, 'config.ini'))

    logging.basicConfig(format='%(asctime)s - %(levelname)s %(message)s', filename=os.path.join(base_path, 'ddns.log'), level=logging.DEBUG)

    ip_endpoint = config['DEFAULT']['ip_endpoint']
    ddns_endpoint = config['DEFAULT']['ddns_endpoint']
    current_ip = config['DEFAULT']['current_ip']
    hostname = config['DEFAULT']['hostname']
    user = config['DEFAULT']['user']
    password = config['DEFAULT']['password']


    response_ip = requests.get(ip_endpoint)

    if(response_ip.status_code == 200):
        ip = response_ip.text.strip()

        if(ip == current_ip):
            logging.info("IP still the same, exiting...")
            return

        headers = {'User-Agent': 'homeserver-ddns'}        
        params = (('hostname', hostname),('myip', ip))

        response_ddns = requests.post(ddns_endpoint, auth=(user, password), headers=headers, params=params)

        logging.info(response_ddns.text)
        if(response_ddns.text == "good " + ip) or (response_ddns.text == "nochg " + ip):
            logging.info("Sucess")
            config['DEFAULT']['current_ip'] = ip

            with open(os.path.join(base_path, 'config.ini'), 'w') as configfile:
                config.write(configfile)
        elif(response_ddns.text == "911"):
            logging.error("Error in endpoint, waiting 5 minutes")
            time.sleep(60*5) #5 minutes
            run() #recursive
        else:
            logging.error("Error")

    else:
        logging.error("Error")
        return

if(__name__ == "__main__"):
    run()