#!/usr/bin/python3
import os
import toml
import subprocess as sub

config = toml.load('confdpdkinit.toml')

# chargement des drivers
sub.run(["modprobe igb_uio"], shell=True)

# mappage des NIC sur dpdk

for nic in config['nic']:
    bind = 'dpdk-devbind --force  --bind=' + nic['driver'] + ' ' + nic['adresse']
    sub.run([bind], shell=True)

# configuration du switch

# creation du switch

for br in config['switch']:
    # RAZ
    delete = 'ovs-vsctl del-br ' + br['nom']
    sub.run([delete], shell=True)
    # creation
    create = 'ovs-vsctl add-br ' + br['nom'] +' -- set bridge '+br['nom']+' datapath_type='+br['datapath_type']
    print(create)
    sub.run([create], shell=True)

# creation & configuration  des ports

    for port in br['port']:
        addport = 'ovs-vsctl add-port ' + br['nom'] + ' ' + port['nom']
        portconfiguration = ''
        #print(addport)
        #sub.run([addport], shell=True)
        if port['type'] == 'dpdk':
            for nic in config['nic']:
                if nic['switch'] == br['nom'] and nic['nomport'] == port['nom']:
                    portconfiguration = nic[
                        'nomport'] + ' ' + 'type=dpdk options:dpdk-devargs=' + nic['adresse']
                    addetconf = addport + ' -- set Interface ' + portconfiguration
                    sub.run([addetconf], shell=True)
        elif port['type'] == 'internal':
            portconfiguration = port['nom'] + ' ' + 'type=internal'
            addetconf = addport + ' -- set Interface ' + portconfiguration
            sub.run([addetconf], shell=True)

# interface up
    ipassign = 'ip addr add 192.168.220.140/24  dev ' + br['nom']
    sub.run([ipassign], shell=True)
    brup = 'ip link set '+br['nom']+' up'
    print(brup)
    sub.run([brup], shell=True)
    for port in br['port']:
        if port["type"] == 'internal':
            ipassign ='ip addr add 192.168.220.134/24  dev '+port['nom']
            sub.run([ipassign], shell=True)
            portup = 'ip link set '+port['nom']+' up'
            print(portup)
            sub.run([portup], shell=True)
