#Enhances the AlphaFill results table with ligand names
#ligands name files can be generated with build_ligand_info.py
import json
import os


#Adds ligands names to the AlphaFill results table
def add_ligand_names(ligand_info_file, table, output_suffix="ligand_names"):

    table_name = os.path.splitext(os.path.basename(table))[0]
    new_table = ""

    with open(ligand_info_file, "r") as json_file:
        ligand_info = json.load(json_file)

    with open(table, "r") as f:
        for l in f:
            line = l.strip().split("\t")
            new_table += line[0] + "\t"
            for ligand in line[1:]:
                if len(ligand.split()) == 1:
                    new_table += ligand + "; " + ligand_info[ligand].replace(" ","_") + "\t"
                else:
                    new_table += ligand + "; " + ligand_info[ligand.split()[0]].replace(" ","_") + "\t"
            new_table = new_table.strip() + "\n"
            
    if output_suffix != "":
        with open(f"{table_name}_{output_suffix}.tsv", "w") as f:
            f.write(new_table)
    else:
        with open(f"{table_name}.tsv", "w") as f:
            f.write(new_table)

add_ligand_names(
                ligand_info_file="ligands_info.json",
                table="AlphaFill_results.tsv",
                )
