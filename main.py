#!/usr/bin/env python
import sys, os, yaml, copy, getopt
from novaclient.client import Client

def usage():
    print("usage: main.py [-c CONFIG_PATH] <create|delete>")

def get_nova_client():
    creds = {}
    creds['version'] = '2'
    creds['username'] = os.environ['OS_USERNAME']
    creds['password'] = os.environ['OS_PASSWORD']
    creds['auth_url'] = os.environ['OS_AUTH_URL']
    creds['project_id'] = os.environ['OS_TENANT_ID']
    return Client(**creds)

def merge(d1, d2):
    for k in d2:
        if k in d1 and isinstance(d1[k], dict) and isinstance(d2[k], dict):
            merge(d1[k], d2[k])
        else:
            d1[k] = d2[k]

def make_srv(default, srv):
    res = copy.deepcopy(default)
    merge(res, srv)
    if set(res.keys()) != set(["image", "flavor", "network", "instances-nb", "meta"]):
        raise BaseException("invalid server: " + str(res))
    return res
 
def read_config_file(config_file_path):
    with open(config_file_path, "r") as stream:
        try:
            return yaml.load(stream)
        except yaml.YAMLError as exc:
            print(exc)

def create(config_file_path):
    nova = get_nova_client()

    if len(nova.servers.list()) > 0:
        raise BaseException("Some servers are already running")

    # read config
    config = read_config_file(config_file_path)
    default_srv = make_srv({"meta": {}, "instances-nb": 1}, config["default"])

    # make a list of server types
    servers_types = []
    for k, v in config["servers"].items():
        srv = make_srv(default_srv, v)
        srv["name"] = k
        servers_by_name.append(srv)

    # make a list of server instances
    servers = []
    for srv in servers_by_name:
        instances_nb = srv["instances-nb"]
        srv.pop("instances-nb", None)
        for i in range(0, instances_nb):
            new_srv = copy.deepcopy(srv)
            if instances_nb != 1:
                new_srv["name"] = new_srv["name"] + "-" + str(i)
            servers.append(new_srv)

    # populate instances with nova objects
    for srv in servers:
        srv["image"] = nova.glance.find_image(name_or_id=srv["image"])
        srv["flavor"] = nova.flavors.find(name=srv["flavor"])
        srv["network"] = nova.neutron.find_network(name=srv["network"])

    # send creation command
    for srv in servers:
        print("creating " + srv["name"] + "...")
        nova.servers.create(**srv)

def delete_all():
    nova = get_nova_client()
    for s in nova.servers.list():
        print("deleting " + s.name + "...")
        nova.servers.delete(s)

# read command line
try:
    opts, args = getopt.getopt(sys.argv[1:], "c:")
except getopt.GetoptError as err:
    print(str(err))
    usage()
    sys.exit(2)

# process options
config_file_path = "config.yml"
for o, a in opts:
    if o == "-c":
        config_file_path = a

# process arguments
if len(args) != 1:
    usage()
    sys.exit(2)
elif args[0] == "create":
    create(config_file_path)
elif args[0] == "delete":
    delete_all()
else:
    usage()
    sys.exit(1)
