import random
import os
import csv
import re

# Configuration
NETWORK = "172.16.5.0/24"
LAB_CONF_PATH = "lab.conf"

# Générer une IP aléatoire
def is_ip_available(ip_address):
    """Vérifie si l'adresse IP est déjà attribuée."""
    if not os.path.exists(LAB_CONF_PATH):
        return True
    with open(LAB_CONF_PATH, "r") as lab_conf:
        for line in lab_conf:
            if ip_address in line:
                return False
    return True

def generate_random_ip():
    """Génère une IP aléatoire."""
    while True:
        base_ip = NETWORK.split('/')[0].split('.')
        base_ip[-1] = str(random.randint(3, 254))
        ip_address = '.'.join(base_ip)
        if is_ip_available(ip_address):
            return ip_address

# Ajouter une nouvelle machine
def add_to_lab_conf(machine_name, ip_address):
    """Ajoute une machine au fichier lab.conf et crée son fichier startup."""
    try:
        with open(LAB_CONF_PATH, "a") as lab_conf:
            lab_conf.write(f"{machine_name}[0]=net1\n")
        print(f"Machine '{machine_name}' ajoutée au réseau avec l'IP {ip_address}.")
    except Exception as e:
        print(f"Erreur lors de l'ajout au fichier lab.conf : {e}")

def create_startup_file(machine_name, ip_address):
    """
    Crée le fichier startup pour configurer la machine avec ou sans blocage DNS.
    """
    startup_path = f"{machine_name}.startup"
    try:
        with open(startup_path, "w") as startup:
            startup.write(f"""#!/bin/bash
ip address add {ip_address}/24 dev eth0
ip link set dev eth0 up
ip route add default via 172.16.5.254
echo 'nameserver 172.16.5.254' > /etc/resolv.conf\n
""")
        print(f"Fichier startup créé pour '{machine_name}'.")
    except Exception as e:
        print(f"Erreur lors de la création du fichier startup : {e}")


# Programme principal
def main():
    print("=== Ajouter une Nouvelle Connexion ===")
    first_name = input("Entrez votre prénom : ").strip()
    last_name = input("Entrez votre nom : ").strip()

    machine_name = f"{first_name}_{last_name}".lower()
    ip_address = generate_random_ip()

    # Ajouter la machine au réseau
    add_to_lab_conf(machine_name, ip_address)

    # Créer le fichier startup pour la machine
    create_startup_file(machine_name, ip_address)


    print(f"Connexion pour {first_name} {last_name} créée avec succès.")
    print(f"Machine : {machine_name}")
    print(f"Adresse IP : {ip_address}")

if __name__ == "__main__":
    main()
