#You can download the ligand info in .CSV format from https://www.rcsb.org/
#This simple script iterates over the files and builds JSON file
#The JSON files contains all unique ligand IDs and Names
import glob

Ligand_ID = 0
Ligand_Name = 0 

ligands_dict = {}

ligands = "{\n"
for file in glob.glob("*.csv"):
    with open(file, "r") as f:
        for l in f:
            line = l.split(",")
            if len(line) > 6:
                if Ligand_ID != 0 and Ligand_Name != 0:
                    if not line[Ligand_ID].strip('"') in ligands_dict:
                        ligands_dict[line[Ligand_ID].strip('"')] = line[Ligand_Name].strip('"')
                if "Ligand ID" and "Ligand Name" in l:
                    Ligand_ID = line.index("Ligand ID")
                    Ligand_Name = line.index("Ligand Name")
    Ligand_ID, Ligand_Name = 0, 0

for k, v in ligands_dict.items():
    ligands += f'\t"{k}" : "{v}",\n'
ligands = ligands.strip(",\n")           
ligands += "\n}"

with open("ligands_info.json", "w") as f:
    f.write(ligands)
