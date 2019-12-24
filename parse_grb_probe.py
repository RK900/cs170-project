import os
from datetime import date
import sys
import subprocess


def print_grb_url(key):
    p = subprocess.Popen(
        ['grbprobe'],
        stdout=subprocess.PIPE
    )
    keys = {}
    for line in p.stdout.readlines()[1:]:
        res = line.decode('utf-8').strip().split("=")
        keys[res[0]] = res[1]


    url = "https://apps.gurobi.com/keyserver?id={key}&hostname={hostname}&hostid={hostid}&username={username}&os={os}&sockets=1&cpu={cpu}&localdate={today}&version=9".format(hostname=keys["HOSTNAME"], hostid=keys["HOSTID"], username=keys["USERNAME"], os=keys["PLATFORM"], cpu=keys["CPU"], today=date.today(),key=key)
    print(url)

if __name__ == "__main__":
    key = "<insert key>"
    if len(sys.argv) >= 2:
        key = sys.argv[1]
    print_grb_url(key)