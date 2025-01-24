from scapy.all import sniff, TCP, IP, UDP, DNS
import csv
from datetime import datetime
import os

# Chemin du fichier CSV pour enregistrer les connexions
CSV_FILE = "/shared/network_connections.csv"

# Fichier contenant les domaines bloqués (à configurer dans dnsmasq)
BLOCKED_DOMAINS_FILE = "/etc/dnsmasq.d/blocked_urls.conf"

# Charger les domaines bloqués depuis dnsmasq
def load_blocked_domains():
    """Charge les domaines bloqués depuis le fichier dnsmasq."""
    blocked_domains = set()
    try:
        with open(BLOCKED_DOMAINS_FILE, "r") as file:
            for line in file:
                if line.startswith("address=/"):
                    domain = line.split("/")[1]
                    blocked_domains.add(domain.strip())
    except FileNotFoundError:
        print(f"Fichier {BLOCKED_DOMAINS_FILE} introuvable. Aucun domaine bloqué chargé.")
    return blocked_domains

# Initialiser le fichier CSV
def initialize_csv(file_path):
    """Crée le fichier CSV avec des en-têtes si ce n'est pas déjà fait."""
    try:
        with open(file_path, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Timestamp", "Source IP", "Destination IP", 
                             "Source Port", "Destination Port", "Protocol", "Destination Domain", "Blocked"])
        print(f"Fichier CSV {file_path} initialisé.")
    except Exception as e:
        print(f"Erreur lors de l'initialisation du fichier CSV : {e}")

# Écrire les données dans le fichier CSV
def write_to_csv(file_path, data):
    """Écrit une ligne de données dans le fichier CSV."""
    try:
        with open(file_path, mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(data)
    except Exception as e:
        print(f"Erreur lors de l'écriture dans le fichier CSV : {e}")

# Callback pour traiter les paquets capturés
def process_packet(packet, blocked_domains):
    """Extrait les informations importantes des paquets capturés."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    src_ip, dst_ip, src_port, dst_port, protocol, domain, blocked = None, None, None, None, "Other", None, "No"

    # Récupérer les informations IP
    if packet.haslayer(IP):
        src_ip = packet[IP].src
        dst_ip = packet[IP].dst

    # Récupérer les informations TCP/UDP
    if packet.haslayer(TCP):
        protocol = "TCP"
        src_port = packet[TCP].sport
        dst_port = packet[TCP].dport
    elif packet.haslayer(UDP):
        protocol = "UDP"
        src_port = packet[UDP].sport
        dst_port = packet[UDP].dport

    # Récupérer les informations DNS (si disponibles)
    if packet.haslayer(DNS) and packet[DNS].qr == 0:  # Si c'est une requête DNS
        domain = packet[DNS].qd.qname.decode("utf-8").strip(".")
        # Vérifier si le domaine est bloqué
        if domain in blocked_domains:
            blocked = "Yes"

    # Afficher les données capturées (facultatif)
    print(f"[{timestamp}] ({src_ip}:{src_port}) -> {dst_ip}:{dst_port} ({protocol}) Domain: {domain} Blocked: {blocked}")

    # Écrire les données dans le fichier CSV
    write_to_csv(CSV_FILE, [timestamp,  src_ip, dst_ip, src_port, dst_port, protocol, domain, blocked])

# Fonction principale
def main():
    """Initialise le fichier CSV, charge les données et démarre la capture de paquets."""
    print("Initialisation...")
    initialize_csv(CSV_FILE)

    blocked_domains = load_blocked_domains()

    print("Capture des paquets réseau...")
    # Capture les paquets sur une interface spécifique (par exemple eth0)
    sniff(iface="eth0", filter="ip", prn=lambda pkt: process_packet(pkt, blocked_domains), store=False)

if __name__ == "__main__":
    main()
