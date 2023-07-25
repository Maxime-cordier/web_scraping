from bs4 import BeautifulSoup
import requests, string, math, os

# main
def main():
    URL = "https://skybrary.aero"
    webSite = requests.get(URL)
    soup = BeautifulSoup(webSite.content, "html.parser")
    elements = soup.find_all("div", class_="term-name")

    num_files = 0

    for element in elements:
        URL_element = URL + element.find("a")["href"]
        webSite_element = requests.get(URL_element)
        soup_element = BeautifulSoup(webSite_element.content, "html.parser")

        div_element_articles = soup_element.find_all("div", class_="title")
        span_element_articles = soup_element.find_all("span", class_="field-content")
        element_articles = div_element_articles + span_element_articles

        for element_article in element_articles:
            URL_article = URL + element_article.find("a")["href"]
            webSite_article = requests.get(URL_article)
            soup_article = BeautifulSoup(webSite_article.content, "html.parser")

            group_items = soup_article.find("div", class_="group-left-bottom")
            
            
            """# Parcourir le contenu HTML pour afficher les balises <h2> et <p>
            current_h2 = None

            for tag in group_items.find_all(['h2', 'p']):
                if tag.name == 'h2':
                    # Afficher le contenu de la balise <h2>
                    current_h2 = tag.text.strip()
                    print(f"\n<h2>{current_h2}</h2>")
                elif tag.name == 'p':
                    # Afficher le contenu de la balise <p> associée au dernier <h2>
                    if current_h2 is not None:
                        print(tag.text.strip())"""
            
            # Initialiser un dictionnaire pour stocker le contenu des <h2> et <p>
            data_dict = {}

            # Parcourir le contenu HTML pour récupérer le contenu des <h2> et <p>
            current_h2 = None
            current_p = []
            for tag in group_items.find_all(['h2', 'p']):
                if tag.name == 'h2':
                    # Enregistrer le contenu du dernier <h2> et ses <p> associés
                    if current_h2 is not None and current_p:
                        data_dict[current_h2] = current_p

                    # Mettre à jour la valeur du dernier <h2>
                    current_h2 = tag.text.strip()

                    # Réinitialiser la liste des <p> associés au nouveau <h2>
                    current_p = []
                elif tag.name == 'p':
                    # Ajouter le contenu du <p> à la liste en cours
                    current_p.append(tag.text.strip())

            # Sauvegarder le dernier <h2> et ses <p> associés (s'il y en a)
            if current_h2 is not None and current_p:
                data_dict[current_h2] = current_p

            # Écrire les données dans des fichiers .txt
            for h2, p_content in data_dict.items():
                # Utiliser le nom du fichier basé sur la valeur de <h2> (sans caractères invalides)
                filename_prefix = f"{h2.translate(str.maketrans('', '', string.punctuation))}"

                # Limiter le contenu de <p> à 500 mots par fichier
                words_limit = 500
                total_words = len(" ".join(p_content).split())
                num_files = math.ceil(total_words / words_limit)

                for i in range(num_files):
                    # Sélectionner les mots pour chaque fichier
                    start_idx = i * words_limit
                    end_idx = (i + 1) * words_limit
                    words = " ".join(p_content).split()[start_idx:end_idx]

                    # Construire le contenu du fichier
                    file_content = " ".join(words)

                    # Numéroter le fichier s'il y a plus d'un fichier
                    if num_files > 1:
                        filename = f"/{filename_prefix}_{i+1}.txt"
                    else:
                        filename = f"/{filename_prefix}.txt"

                    # Si répertoire element_article.text n'existe pas alors le créer
                    main_directory_name = f"{element.text.translate(str.maketrans('', '', string.punctuation))}"
                    if os.path.exists(main_directory_name) == False:
                        os.mkdir(main_directory_name)


                    # Si répertoire element_article.text n'existe pas alors le créer
                    directory_name = f"{element_article.text.translate(str.maketrans('', '', string.punctuation))}"
                    if os.path.exists(main_directory_name+"/"+directory_name) == False:
                        os.mkdir(main_directory_name+"/"+directory_name)


                    # Écrire le contenu dans le fichier .txt
                    with open(main_directory_name +"/"+ directory_name + filename, 'w', encoding='utf-8') as file:
                        file.write(file_content)
                        num_files = num_files+1
        
    print("Generated files: "+str(num_files))
      
# run main
if __name__ == "__main__":
    main()
