import csv
import json
import os
import platform
import socket
import subprocess
import pandas as pd
import psutil

# ==============================================================================
# 1. HARDWARE & BESTURINGSSYSTEEM (Opdracht 1 & 2)
# ==============================================================================
hostname = socket.gethostname()
computermodel = platform.machine()
processor = platform.processor()
physical_cores = psutil.cpu_count(logical=False)

cpu_freq = psutil.cpu_freq()
max_freq_mhz = cpu_freq.max if cpu_freq else 0.0

# RAM naar GB omrekenen
ram_total_gb = round(psutil.virtual_memory().total / (1024**3), 2)

# Opslag primaire systeemschijf
primary_mount = "C:\\" if os.name == "nt" else "/"
storage_usage = psutil.disk_usage(primary_mount)
storage_total_gb = round(storage_usage.total / (1024**3), 2)

disk_parts = psutil.disk_partitions(all=False)
storage_fstype = next(
    (p.fstype for p in disk_parts if p.mountpoint == primary_mount), "Unknown"
)

# Netwerkinterface detecteren
net_addrs = psutil.net_if_addrs()
net_stats = psutil.net_if_stats()

primary_iface = "Niet gedetecteerd"
mac_address = "Onbekend"
ipv4_address = "Onbekend"
ipv6_address = "Onbekend"
ipv6_link_local = "Onbekend"

for iface_name, addrs in net_addrs.items():
  is_up = net_stats[iface_name].isup if iface_name in net_stats else False
  has_valid_ipv4 = any(
      a.family == socket.AF_INET
      and not a.address.startswith("127.")
      and not a.address.startswith("169.254.")
      for a in addrs
  )

  if is_up and has_valid_ipv4:
    primary_iface = iface_name
    for a in addrs:
      if a.family == psutil.AF_LINK:
        mac_address = a.address
      elif a.family == socket.AF_INET:
        ipv4_address = a.address
      elif a.family == socket.AF_INET6:
        if a.address.startswith("fe80"):
          ipv6_link_local = a.address.split("%")[0]
        else:
          ipv6_address = a.address
    break

# ==============================================================================
# 2. OPDRACHT 8: SERIENUMMER VAN HET SYSTEEM OPHALEN
# ==============================================================================
serial_number = "Onbekend"
try:
  serial_output = subprocess.check_output(
      "powershell (Get-CimInstance Win32_BIOS).SerialNumber",
      shell=True,
      text=True,
  )
  serial_number = serial_output.strip()
except Exception:
  try:
    serial_output = subprocess.check_output(
        "wmic bios get serialnumber", shell=True, text=True
    )
    serial_number = serial_output.split("\n")[1].strip()
  except Exception:
    pass

# ==============================================================================
# 3. DICTIONARY SAMENSTELLEN (Inclusief Serienummer)
# ==============================================================================
filtered_sysinfo = {
    "computernaam": hostname,
    "serienummer": serial_number,
    "computermodel": computermodel,
    "processor": processor,
    "fysieke_cores": physical_cores,
    "max_cpu_freq_mhz": max_freq_mhz,
    "ram_totaal_gb": ram_total_gb,
    "opslag_bestandssysteem": storage_fstype,
    "opslag_capaciteit_gb": storage_total_gb,
    "primaire_netwerkinterface": primary_iface,
    "mac_adres": mac_address,
    "ipv4_adres": ipv4_address,
    "ipv6_adres": ipv6_address,
    "ipv6_link_local": ipv6_link_local,
}

# ==============================================================================
# 4. EXPORT NAAR JSON, CSV EN EXCEL (Opdracht 3, 4 & 5)
# ==============================================================================
# Sluit Excel op je computer als je sysinfo.xlsx open hebt staan!
with open("sysinfo.json", "w", encoding="utf-8") as f:
  json.dump(filtered_sysinfo, f, indent=2)

with open("sysinfo.csv", "w", newline="", encoding="utf-8") as f:
  writer = csv.DictWriter(f, fieldnames=list(filtered_sysinfo.keys()))
  writer.writeheader()
  writer.writerow(filtered_sysinfo)

df = pd.DataFrame([filtered_sysinfo])
df.to_excel("sysinfo.xlsx", index=False)

print(
    "Opdracht 1 t/m 5 én Opdracht 8 succesvol uitgevoerd met serienummer!\n"
)
print(json.dumps(filtered_sysinfo, indent=2))