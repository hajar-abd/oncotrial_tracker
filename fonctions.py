###########################################################################################################################################
#charger les packages
import pandas as pd
import re
import xml.etree.ElementTree as ET
###########################################################################################################################################

#charger le fichier XML MeSH
tree = ET.parse("desc2024.xml") #doit etre au meme niveau que le fichier ou preciser le chemin
root = tree.getroot()

#code MeSH de Neoplasms
mesh_code = "C04"
mesh_dict = {} #utiliser dans le script dataframe

#construire un dictionnaire des correspondances code -> nom
mesh_categories = {}
for descriptor in root.findall("DescriptorRecord"):
    descriptor_name = descriptor.find("DescriptorName/String").text
    for tree_number in descriptor.findall(".//TreeNumber"):
        mesh_categories[tree_number.text] = descriptor_name  # Associe le code à son nom

#construire le dictionnaire des sous-categories
for descriptor in root.findall("DescriptorRecord"):
    descriptor_name = descriptor.find("DescriptorName/String").text
    categories = []

    for tree_number in descriptor.findall(".//TreeNumber"):
        if tree_number.text and tree_number.text.startswith(mesh_code + "."):
            categories.append(tree_number.text)

    if categories:
        #extraire la categorie parent (ex: "C04.588.123" -> "C04.588")
        first_sublevel = categories[0][:7]  #prend les 7 premiers caracteres "C04.XXX"

        #recuperer directement le nom du parent sans boucle
        parent_name = mesh_categories.get(first_sublevel)

        if parent_name:
            mesh_dict.setdefault(parent_name, []).append(descriptor_name)


######################################

def study_mesh(study):
    #recuperer tous les mesh terms cites
    mesh = []
    ancestror = []
    if study.get("derivedSection") is not None and study["derivedSection"].get("conditionBrowseModule") is not None:
        if study["derivedSection"]["conditionBrowseModule"].get("meshes") is not None:
            mesh = [i["term"] for i in study["derivedSection"]["conditionBrowseModule"]["meshes"]]
        if study["derivedSection"]["conditionBrowseModule"].get("ancestors") is not None:
            ancestror = [i["term"] for i in study["derivedSection"]["conditionBrowseModule"]["ancestors"]]
    return mesh + ancestror

######################################

def extract_year(date_str):
    #extrait uniquement l'annee d'une date sous differents formats
    match = re.search(r'\d{4}', str(date_str))  #cherche une annee a 4 chiffres
    return int(match.group()) if match else None


def parse_date(date_str):
    try:
        # Si la date est complète (YYYY-MM-DD)
        return pd.to_datetime(date_str, format="%Y-%m-%d", errors='coerce')
    except:
        # Si la date est incomplète (YYYY-MM), on ajoute le premier jour du mois
        try:
            return pd.to_datetime(date_str + "-01", format="%Y-%m-%d", errors='coerce')
        except:
            return None
