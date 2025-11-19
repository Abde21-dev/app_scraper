from flask import Flask, request, render_template
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# ---- Fonction générique de scraping ----
def scrape_page(url: str) -> str:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "fr-FR,fr;q=0.9"
    }

    response = requests.get(url, headers=headers, timeout=10)
    if response.status_code != 200:
        raise Exception(f"Erreur HTTP {response.status_code} lors du téléchargement de la page.")

    html = response.text
    soup = BeautifulSoup(html, "html.parser")

    # On récupère tout le texte des balises <p>
    paragraphes = soup.find_all("p")

    texte_final = ""
    for p in paragraphes:
        texte = p.get_text(strip=True)
        if texte:
            texte_final += texte + "\n\n"

    if not texte_final.strip():
        raise Exception("Aucun texte exploitable trouvé dans cette page.")

    return texte_final


# ---- Route principale avec formulaire ----
@app.route("/", methods=["GET", "POST"])
def index():
    texte = None
    erreur = None
    url_saisie = ""

    if request.method == "POST":
        url_saisie = request.form.get("url", "").strip()

        if not url_saisie:
            erreur = "Merci d'indiquer une URL."
        else:
            # On ajoute automatiquement le schéma si l'utilisateur oublie (ex : 'example.com')
            if not url_saisie.startswith(("http://", "https://")):
                url_saisie = "https://" + url_saisie

            try:
                texte = scrape_page(url_saisie)
            except Exception as e:
                erreur = f"Une erreur est survenue lors du scraping : {e}"

    return render_template("index.html", texte=texte, erreur=erreur, url_saisie=url_saisie)


if __name__ == "__main__":
    app.run(debug=True)
