#You can download the ligand info files in .json format from https://www.rcsb.org/
#This simple script iterates over the files and builds JSON file
#The JSON files contains all unique ligand IDs and Names
import glob

ligands_dict = {}

id_value = ""
name_value = ""

for file in glob.glob("./*.json"):
    with open(file, "r") as f:
        for l in f:
            if '"id"' in l:
                id_value = l.split('"')[-2]
            if '"name"' in l:
                name_value = l.split('"')[-2]
                ligands_dict[id_value] = name_value

ligands = "{\n"
for k, v in ligands_dict.items():
    v = v.replace('"',"'").strip()
    ligands += f'\t"{k}" : "{v}",\n'
ligands = ligands.strip(",\n")           
ligands += "\n}"

with open("ligands_info.json", "w") as f:
    f.write(ligands)
