from resources.ip import open5gsIP
commands = [
    'ps-establish',
    'ps-list',
    'ps-release',
    'ps-release-all',
    'deregister normal',
    #'ps-establish IPv4 --emergency',
    'ps-establish IPv4 --sst 1 --sd 16777215 --dnn internet'
]

commands_id = [2, 3, 4, 5]

csrf_url = "http://" + open5gsIP + ":3000/api/auth/csrf"
headers_ = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
}

login_url = "http://" + open5gsIP + ":3000/api/auth/login"
login_data = "{\"username\": \"admin\", \"password\": \"1423\"}"
headers_post = {
    "Content-Type": "application/json",
    "User-Agent": headers_["User-Agent"],
    "X-CSRF-TOKEN": "",
    "Cookie": ""
}
session_url = "http://" + open5gsIP + ":3000/api/auth/session"
headers_hascookie = {
    "User-Agent": headers_["User-Agent"],
    "Cookie": ""
}

subscriber_url = "http://" + open5gsIP + ":3000/api/db/Subscriber"
headers_auth = {
    "Content-Type": headers_post["Content-Type"],
    "User-Agent": headers_["User-Agent"],
    "X-CSRF-TOKEN": "",
    "Cookie": "",
    "Authorization": "Bearer "
}


data1 = '{"imsi": "208930000000004","security": {"k": "465B5CE8 B199B49F AA5F0A2E E238A6BC","amf": "8000","op_type": 0,"op_value": "E8ED289D EBA952E4 283B54E8 8E6183CA","op": null,"opc": "E8ED289D EBA952E4 283B54E8 8E6183CA"},"ambr": {"downlink": {"value": 1,"unit": 3},"uplink": {"value": 1,"unit": 3}},"slice": [{"sst": 1,"default_indicator": true,"session": [{"name": "internet", "type": 3,"ambr": {"downlink": {"value": 1,"unit": 3},"uplink": {"value": 1,"unit": 3}},"qos": {"index": 9,"arp": {"priority_level": 8,"pre_emption_capability": 1,"pre_emption_vulnerability": 1}}}]}]}'

