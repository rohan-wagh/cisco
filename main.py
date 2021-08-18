from flask_reggie import Reggie
from flask import Flask, jsonify, render_template, request
from netmiko import ConnectHandler


# Instantiate Flask app
app = Flask(__name__, template_folder='templates')
Reggie(app)


# In memory DB for testing purpose
interfaceDB = [
    {
        'interface': 'GigabitEthernet',
        'ip_address': '172.16.2.1',
        'subnet': '255.255.255.0',
        'status': 'Active'
    },
]


# Base URL for taking interface input form
@app.route("/")
def index():
    return render_template('interface_form.html')


# Api for getting single interface according to the it's name.
@app.route('/interface/<name>/', methods=['GET'])
def getInterface(name):
    client = ConnectHandler("localhost", port=10048, username="tester", password="admin", device_type='cisco_ios')
    client.enable()
    output = client.send_command('show running-config', use_textfsm=True)
    op_list = output.split("\n")
    data = {}
    li = []
    for item in op_list:
        if "!" in item:
            if bool(data):
                li.append(data)
            data = {}
        if "interface" in item:
            data["interface"] = item.split(" ")[1]
        if "description" in item:
            data["description"] = item.replace(" description ", "")
        if "ip address" in item and "no ip address" not in item:
            data["ip address"] = item.split(" ")[3]
        if "clock rate" in item:
            data["clock rate"] = item.split(" ")[3]
        if "duplex" in item:
            if len(item.split(" ")) == 3:
                data["duplex"] = item.split(" ")[2]
        if "speed" in item:
            data["speed"] = item.split(" ")[2]
    interface = [i for i in filter(lambda x: x['interface'] == name, li)][0]
    return jsonify({"data": interface})


# Api for adding single interface.
@app.route('/interface/add', methods=['POST'])
def addInterface():
    try:
        result = request.form
        data = {
            'interface': result['interface'],
            'ip_address': result['ip_address'],
            'subnet': result['subnet'],
            'status': result['status']
        }
        interfaceDB.append(data)
        return render_template("interfaces_details.html", result=result)
    except Exception as e:
        return jsonify({'data': "An error occurred while adding the interface."})


# Api for getting all interface blocks
@app.route('/interface/blocks', methods=['GET'])
def interfaceBlocks():
    client = ConnectHandler("localhost", port=10048, username="tester", password="admin",  device_type='cisco_ios')
    client.enable()
    output = client.send_command('show running-config', use_textfsm=True)
    op_list = output.split("\n")
    data = {}
    li = []
    for item in op_list:
        if "!" in item:
            if bool(data):
                li.append(data)
            data = {}
        if "interface" in item:
            data["interface"] = item.split(" ")[1]
        if "description" in item:
            data["description"] = item.replace(" description ","")
        if "ip address" in item and "no ip address" not in item:
            data["ip address"] = item.split(" ")[3]
        if "clock rate" in item:
            data["clock rate"] = item.split(" ")[3]
        if "duplex" in item:
            if len(item.split(" ")) == 3:
                data["duplex"] = item.split(" ")[2]
        if "speed" in item:
            data["speed"] = item.split(" ")[2]
    return jsonify({"data":li})


if __name__ == "__main__":
    app.run()
