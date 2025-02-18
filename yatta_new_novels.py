from bs4 import BeautifulSoup as bs
import requests
from datetime import datetime
import pandas as pd
import os
import subprocess
import time


#Link to Yatta Tachi Resources. We're looking for the first link that points to the novel and manga releases for the month.
YATTA = "https://yattatachi.com/category/resources"
FOLDER = "YattaTachi" # Change this to your preferred folder name, only using that because that's what the folder name I used was

def make_folders():
    if not os.path.exists("images"):
        os.makedirs("images")
    if not os.path.exists(FOLDER):
        os.makedirs(FOLDER)


def save_img(book_img_link, book_title):
    print("[INFO] Sleeping for 5 seconds to respect robots.txt")
    time.sleep(5)
    extension = os.path.splitext(book_img_link)[1]
    filename = os.path.join("images", f"{book_title}{extension}")
    print("[INFO] Saving image: " + filename)
    forbidden_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    safe_filename = ''.join(c if c not in forbidden_chars else '_' for c in book_title)
    filename = os.path.join("images", f"{safe_filename}{extension}")
    cmd = ['wget', '-O', filename, book_img_link]
    subprocess.Popen(cmd).communicate()
    
    
    

def tag_releases(title:str)->str: 
    if title.__contains__("Azuki") and title.__contains__("Chapter") or title.__contains__("NOOK Edition") and title.__contains__("#"):
        tag ="Individual Chapter Release"
        # print(f"[INFO] '{title}' is an Individual Chapter Release")
    elif title.__contains__("NOOK Edition"):
        tag = "NOOK Edition Release"
        # print(f"[INFO] '{title}' is a NOOK Edition Release")
    else: 
        tag = "None"
        # print(f"[INFO] '{title}' has no tags")
    return tag

def clean_for_search(title:str)->str:
    """
    Cleans a title string by removing certain punctuation characters.

    This function removes the following characters from the input title:
    colon (:), period (.), parentheses (()), ampersand (&), comma (,), and brackets ([]).
    
    Args:
        title (str): The title string to be cleaned.

    Returns:
        str: The cleaned title string with specified characters removed.
    """

    return title.translate(str.maketrans("","",":.()&,[]"))
    
make_folders()

try:
    print("[INFO] Opening Yatta Tachi Resources")
    request = requests.get(YATTA)
    request.raise_for_status()  # Raises an error for bad responses
    content = request.content
    soup = bs(content, "html.parser")
except requests.exceptions.RequestException as e:
    print(f"[ERROR] An error occurred: {e}")


latest_post = soup.find_all("li", class_="post-summary")

print("[INFO] Checking for Manga / Light Novel / Book Releases post")
for post in latest_post:
    if post.text.__contains__("Manga / Light Novel / Book Releases"):
        print("[INFO] Manga / Light Novel / Book Releases post Found:")
        book_release_post = post.text
        book_release_link = post.a["href"]
        print(f"[INFO] Title: {book_release_post}")
        print(f"[INFO] Link: {book_release_link}")
        break

try:
    print(f"[INFO] Opening {book_release_post}: {book_release_link}")
    request = requests.get(book_release_link)
    request.raise_for_status()  # Raises an error for bad responses
    content = request.content
    releases_soup = bs(content, "html.parser")
except requests.exceptions.RequestException as e:
    print(f"[ERROR] An error occurred: {e}")


print("[INFO] Checking for Book Releases")

book_releases = releases_soup.find_all("li", class_="release-single u-ta-c")
book_info = {}
nook_releases = {}
individual_chapters = {}
search_titles = ["===="+book_release_post+"===="] # A way to identify which post we're looking at  



for book in book_releases:
    # print(book)
    # Grab Release Date, format it to YYYY-MM-DD
    book_release_date = str(book).split("data-date=")[1].split(" ")[0].replace('"',"")
    date_string = book_release_date
    date_object = datetime.strptime(date_string, "%B-%d-%Y")
    formatted_date = date_object.strftime("%Y-%m-%d")
    # print(book_release_date)
    # print(formatted_date)
    book_img_link = str(book.find("div", class_="release-img")).split("url(")[1].split(")")[0]
    book_title = book.find("a", class_="release-link").text
    # print(f"[INFO] Processing Book Release {book_title}")
    book_tag = tag_releases(book_title)
    book_release_link = book.find("a", class_="release-link").get("href")
    book_author = book.find("span", class_="release-author").text.split("By ")[1]
    book_release_type = book.find("span", class_="release-type").text
    book_release_company = book.find("span", class_="release-company").text
    clean_title = clean_for_search(book_title)
    book_info_dict = {
        "Date": formatted_date,
        "Title": book_title,
        "Author": book_author,
        "Type": book_release_type,
        "Company": book_release_company,
        "Link": book_release_link,
    }
    if book_tag == "None":
        search_titles.append(clean_title)
        book_info[book_title] = book_info_dict
        save_img(book_img_link, book_title)
    elif book_tag == "NOOK Edition Release":
        nook_releases[book_title] = book_info_dict
    elif book_tag == "Individual Chapter Release":
        individual_chapters[book_title] = book_info_dict
        

df = pd.DataFrame(book_info).T
nook_df = pd.DataFrame(nook_releases).T
ind_chap_df = pd.DataFrame(individual_chapters).T

filename = book_release_post.replace("/","").replace(" ","_")
nook_file = "Nook_Edition_" + filename
ind_chap_file = "Individual_Chapters_" + filename


    

with open(f"{FOLDER}/search.txt", "a") as file:
    for title in search_titles:
        file.write(f"{title}\n")
df.to_csv(f"{FOLDER}/{filename}.csv", index=False, mode='w')
nook_df.to_csv(f"{FOLDER}/{nook_file}.csv", index=False, mode='w')
ind_chap_df.to_csv(f"{FOLDER}/{ind_chap_file}.csv", index=False, mode='w')
print("[INFO] Done, files are in the folder: " + FOLDER)



#TODO Create a Series Title, and Series Index Column. 
#TODO create a file to use for the other script: Search Nyaa for the Release Torrent