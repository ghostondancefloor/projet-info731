import os
import subprocess

def run_command(command):
    try:
        print(f"Running: {command}")
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e}")

# Remonter le système de fichiers en lecture-écriture
run_command("mount -o remount,rw /")

# Activer le NAT
run_command("echo 1 > /proc/sys/net/ipv4/ip_forward")
run_command("iptables -t nat -A POSTROUTING -o eth1 -j MASQUERADE")

# Configurer le DNS avec dnsmasq
dns_config = """
server=8.8.8.8
server=1.1.1.1
listen-address=192.168.141.1
"""
with open("/etc/dnsmasq.conf", "w") as f:
    f.write(dns_config)

# Redémarrer dnsmasq
run_command("/etc/init.d/dnsmasq restart")

# Démarrer xinetd
run_command("/etc/init.d/xinetd start")

# Vérifier la connectivité
run_command("ping -c 2 8.8.8.8")
