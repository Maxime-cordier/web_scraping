from bs4 import BeautifulSoup
import requests, string, math, os

'''
ParserCategory: function that parses all the articles of an alphabatic list.
@param URL: URL of the alphabatic list.
@param name_category: name of the parent repository.
'''
def ParserCategory(URL, name_category):
    
    print("PARSING: "+URL)
    category_page = requests.get(URL+"?items_per_page=100")
    category_soup = BeautifulSoup(category_page.content, "html.parser")
    
    articles=[]

    # TEST: There are more than 1 page if there is a "Go to last page" button
    if category_soup.find("li", class_="pager__item pager__item--last"):
        number_of_pages = int(category_soup.find("a", title="Go to last page")["href"].split("&page=")[1]) +1
        print("(List of articles) Number of pages: "+str(number_of_pages))

        for i in range(int(number_of_pages)):
            category_page = requests.get(URL+"?items_per_page=100&page="+str(i))
            category_soup = BeautifulSoup(category_page.content, "html.parser")
            div_articles = category_soup.find_all("div", class_="title")
            span_articles = category_soup.find_all("span", class_="field-content")
            articles = articles + div_articles + span_articles
    
    else:
        div_articles = category_soup.find_all("div", class_="title")
        span_articles = category_soup.find_all("span", class_="field-content")
        articles = div_articles + span_articles

    print("Number of articles: "+str(len(articles)))
    

    # LOOP: Iterate over all the articles
    for article in articles:
        
        URL_article = "https://skybrary.aero" + article.find("a")["href"]
        webSite_article = requests.get(URL_article)
        soup_article = BeautifulSoup(webSite_article.content, "html.parser")

        print(URL_article)
        
        # Collect all <div> with class="group-left-bottom" (in fact there is only one)
        group_items = soup_article.find_all("div", class_=["group-left-bottom"])

        # TEST: Check if the article is not empty
        if group_items:

            # Sometimes technicals information are available 
            technical_info = group_items[0].find("div", class_="group-technical-data data-table")

            # Sometimes arrays with runways information are available
            runways_information = group_items[0].find("table", class_=["cols-5 airport-runways"])

            # Sometimes arrays with territory airports information are available
            territory_information = group_items[0].find("table", class_="views-table views-view-table cols-5")

            data_dict = {}
            current_h2 = None
            current_p = []

            # Iterate specific tags only in the article
            for tag in group_items[0].find_all(['h2', 'p', 'li', "table", "div"]):
                
                if tag.name == 'h2':
                    # Save in data_dict
                    if current_h2 is not None and current_p:
                        data_dict[current_h2] = current_p

                    current_h2 = tag.text.strip()
                    current_p = []
                
                elif tag.name == 'p':
                    current_p.append(tag.text.strip())

                elif tag.name == 'li':
                    current_p.append(tag.text.strip()+".")
                
                elif tag == technical_info:
                    labels = tag.find_all("div", class_="field-label")
                    values = tag.find_all("div", class_="field-item")
                    for label, value in zip(labels, values):
                        current_p.append(label.text.strip()+": "+value.text.strip()+".")
                
                elif tag == runways_information or tag == territory_information:
                    th_thead = ((tag.find("thead")).find_all("th"))
                    tr_body = ((tag.find("tbody")).find_all("tr"))
                    
                    for tr in tr_body:
                        td = tr.find_all("td")
                        current_p.append("(")
                        for i in range(len(td)):
                            current_p.append(th_thead[i].text.strip()+"="+ td[i].text.strip()+",")
                        current_p.append(") ")
                    
                    #print(current_p)

            # Save the last piece of data
            if current_h2 is not None and current_p:
                data_dict[current_h2] = current_p


            # LOOP: Write content in files text for each couple of h2 and p. 
            for h2, p_content in data_dict.items():
                
                # Get the file name without special characters
                filename_prefix = f"{h2.translate(str.maketrans('', '', string.punctuation))}"

                # Limit the content with 500 mots per file
                words_limit = 500
                total_words = len(" ".join(p_content).split())
                num_files = math.ceil(total_words / words_limit)
                
                # LOOP: Create a file with content (or more than 1 if the content is big)
                for i in range(num_files):
                    
                    start_idx = i * words_limit
                    end_idx = (i + 1) * words_limit
                    words = " ".join(p_content).split()[start_idx:end_idx]
                    file_content = " ".join(words)

                    # Number the file if necessary
                    if num_files > 1:
                        filename = f"/{filename_prefix}_{i+1}.txt"
                    else:
                        filename = f"/{filename_prefix}.txt"

                    # TEST: Data repository creation
                    if os.path.exists("./../data/skybrary_data/"+name_category) == False:
                        os.mkdir("./../data/skybrary_data/"+name_category)

                    # TEST: articles repository creation
                    directory_name = f"{article.text.translate(str.maketrans('', '', string.punctuation))}"
                    if os.path.exists("./../data/skybrary_data/"+name_category+"/"+directory_name) == False:
                        os.mkdir("./../data/skybrary_data/"+name_category+"/"+directory_name)
                    
                    # Write content in the txt file. 
                    with open("./../data/skybrary_data/"+name_category +"/"+ directory_name + filename, 'w', encoding='utf-8') as file:
                        file.write(file_content)
    