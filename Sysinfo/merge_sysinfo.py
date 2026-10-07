import glob
import pandas as pd

print("Zoeken naar CSV-bestanden van groepsleden...")
# Zoek alle sysinfo_*.csv bestanden
files = [
    f for f in glob.glob("sysinfo_*.csv") if "combined" not in f.lower()
]
print(f"Gevonden bestanden: {files}\n")

rename_map = {
    "max_cpu_frequentie": "max_cpu_freq_mhz",
    "totaal_ram_gb": "ram_totaal_gb",
    "bestandssysteem_opslag": "opslag_bestandssysteem",
    "opslagcapaciteit_gb": "opslag_capaciteit_gb",
    "ipv6_link_local_adres": "ipv6_link_local",
}

dfs = []
for file in files:
  with open(file, "r", encoding="utf-8") as f:
    sample = f.read(1024)
    sep = ";" if ";" in sample else ","

  df = pd.read_csv(file, sep=sep)
  df.rename(columns=rename_map, inplace=True)
  dfs.append(df)

if dfs:
  combined_df = pd.concat(dfs, ignore_index=True)
  combined_df.to_csv("combined_sysinfo.csv", index=False)
  combined_df.to_excel("combined_sysinfo.xlsx", index=False)
  print(
      "Succesvol samengevoegd tot combined_sysinfo.csv en"
      " combined_sysinfo.xlsx!\n"
  )
  print(combined_df.to_string())
else:
  print("Geen sysinfo_*.csv bestanden gevonden!")