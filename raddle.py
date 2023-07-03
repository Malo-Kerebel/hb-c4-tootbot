import requests
import re
import json
from bs4 import BeautifulSoup



def get_submissions(community: str) -> list:

    # User agent of a chrome session so raddle accept our request
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}

    r = requests.get(f'https://raddle.me/f/{community}', headers=headers)

    if r.status_code == 200:

        pattern = r'data-submission-id="([^"]+)"'

        content = str(r.content)
        ids = re.findall(pattern, content)

        # Utilisation de BeautifulSoup pour analyser le texte HTML
        soup = BeautifulSoup(content, 'html.parser')

        # Utilisation de expressions régulières pour trouver les valeurs correspondantes
        pattern = r'href="([^"]+)"'
        pic_links = []

        # Parcours de toutes les balises <a> ayant la classe "submission__link"

        for balise_a in soup.find_all('a', class_='submission__link'):
            # Vérification si le motif correspond et extraction de la valeur
            match = re.findall(pattern, str(balise_a))
            if match:
                pic_links.append(match[0])

        return ids, pic_links
    else:
        raise BaseException(f"The request didn't succeed, error {r.status_code}, {r.content}")


def submission_info(community: str, id: str):

    # User agent of a chrome session so raddle accept our request
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}

    r = requests.get(f'https://raddle.me/f/{community}/{id}.json', headers=headers)
    return json.loads(r.content)


if __name__ == "__main__":
    community = "egg_irl"
    ids, urls = get_submissions(community)
    print(submission_info(community, ids[0]))
