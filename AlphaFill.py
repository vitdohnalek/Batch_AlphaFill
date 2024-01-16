#Script for batch AlphaFill predictions using the https://alphafill.eu/ API
#Input is a folder containing pdb/cif files 
#Structure files are enriched by hypothetical ligands
#List of possible ligand binding sites is stored as .tsv file
#JSON file is produced for each structure with all details

import requests
import glob
import time
import json
import os

#Finds values in JSON file
def find_values(json_obj, key):
    values = []
    
    # Check if the current object is a dictionary
    if isinstance(json_obj, dict):
        for k, v in json_obj.items():
            # If the key matches, add the corresponding value to the list
            if k == key:
                values.append(v)
            # If the value is another dictionary, recursively search it
            elif isinstance(v, dict):
                nested_values = find_values(v, key)
                if nested_values is not None:
                    values.extend(nested_values)
            # If the value is a list, iterate through the list and recursively search each element
            elif isinstance(v, list):
                for item in v:
                    nested_values = find_values(item, key)
                    if nested_values is not None:
                        values.extend(nested_values)
    # If the current object is a list, iterate through the list and recursively search each element
    elif isinstance(json_obj, list):
        for item in json_obj:
            nested_values = find_values(item, key)
            if nested_values is not None:
                values.extend(nested_values)
    
    return values if values else None  # Return an empty list if no values found

#Retrives the ligands IDs
def read_JSON(json_file):
    
    #Reads the json data
    with open(json_file) as f:
        data = json.load(f)

    ligands = find_values(data, "analogue_id")

    return ligands

#Connects to the AlphaFill server
#Uploads the structure
#Downloads the CIF results file & JSON file containing all details
def AlphaFill(structure_file):

    #Reads the file name
    file_name = os.path.splitext(os.path.basename(structure_file))[0]

    # Endpoint URL
    url = 'https://alphafill.eu/v1/aff'

    # Read the content of the input structure file
    with open(structure_file, 'r') as file:
        structure_file_content = file.read()

    # Parameters for the POST request
    payload = {
        'structure': structure_file_content,
    }

    #Conditions for while loops
    running_request = True
    status_queued = True

    while running_request:
        # Makes the POST request
        response = requests.post(url, data=payload)

        # Continues when the response is 200
        if response.status_code == 200:
            result = response.json()
            print(f'Success! Job ID: {result["id"]}')

            time.sleep(5) #Not sure if this is needed, it should give time to the server to handle the request

            #Handles the status of the request
            while status_queued:

                #Gets the current status
                status_url = f'https://alphafill.eu/v1/aff/{result["id"]}/status'
                status = requests.get(status_url).json()
                
                
                #In case of error, the prediction for the current model is skipped
                if status['status'] == 'error':
                    print(f'Status: {status["status"]}')
                    status_queued = False
                #Finished status enables the code to continue
                elif status['status'] == 'finished':
                    #print(status)
                    status_queued = False
                #Queued status makes the code wait 30 seconds before another status check
                elif status['status'] == 'queued':
                    print(f"{result['id']} queued")
                    time.sleep(30)
                #Running process makes the code waits 30 seconds before another check
                elif status['status'] == 'running':
                    print(f"{result['id']} running; progress: {status['progress']}")
                    time.sleep(30)
                #In case of anything unexpected the code waits 10 second
                #This might not be needed
                else:
                    print(status)
                    time.sleep(10)

            #Retrives the structure in CIF format
            structure_url = f"https://alphafill.eu/v1/aff/{result['id']}"
            structure = requests.get(structure_url)
            with open(f"{file_name}_AlphaFill.cif", "wb") as cif_file:
                cif_file.write(structure.content)
            
            #retrieves the additional informayion
            json_url = f"https://alphafill.eu/v1/aff/{result['id']}/json"
            json = requests.get(json_url)
            with open(f"{file_name}_AlphaFill.json", "wb") as json_file:
                json_file.write(json.content)
            
        #Handles busy server error by checking the server every 10 seconds
        #Stops the predictions in case of other errors
        else:
            error = response.json()
            if error["error"] == "The server is too busy to handle your request, please try again later":
                print(f'Error: {error["error"]}')
                time.sleep(10)
            else:
                print(f'Error: {error["error"]}')
                running_request = False

        #Everything is done!
        running_request = False
    print(f"Prediction for {file_name} has been processed")

#Runs the predictions with all files in a given folder
def batch_AlphaFill(folder, output_folder="."):

    folder = folder.strip('/')
    for structure_file in glob.glob(f"{folder}/*"):
        AlphaFill(structure_file)

        #Moves the files into a specific folder if requested
        if output_folder != ".":
            output_folder = output_folder.strip('/')
            #Reads the file name
            file_name = os.path.splitext(os.path.basename(structure_file))[0]
            os.system(f"mv {file_name}_AlphaFill.* {output_folder}/")

#Creates a table with all the ligand IDs
def batch_JSON_results(folder, results_name="AlphaFill_results.tsv"):
    
    table_results = ""

    #Iterates over JSON files and appends results to the table
    folder = folder.strip('/')
    for file in glob.glob(f"{folder}/*_AlphaFill.json"):

        file_name = os.path.splitext(os.path.basename(file))[0]
        ligands_info = ""

        ligands = sorted(read_JSON(file))
        unique_ligands = set(ligands)
        #Counts the number of all ligands
        #Sometimes that are multiple ligands of the same kind 
        for unique_ligand in unique_ligands:
            unique_ligand_count = ligands.count(unique_ligand)
            if unique_ligand_count == 1:
                ligands_info += unique_ligand + "\t"
            else:
                ligands_info += unique_ligand + " " + str(unique_ligand_count) + "\t"

        #Appends next row to the results
        table_results += file_name + "\t" + ligands_info.strip("\t") + "\n"

    with open(results_name, "w") as f:
        f.write(table_results)

    print(f"Ligands have been stored in a table {results_name}")

if __name__ == "__main__":
    batch_AlphaFill("INPUT_FOLDER")
    batch_JSON_results("JSON_FOLDER")