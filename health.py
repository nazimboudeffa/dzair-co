import concurrent.futures
import json
import os
import requests
# Désactive les avertissements de sécurité console liés aux certificats SSL ignorés
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Chemins des fichiers
FICHIER_JSON_SOURCE = "sites.json"
FICHIER_JSON_ERREURS = "sites_en_panne.json"


def charger_sites(chemin_fichier):
    """Charge la liste des sites depuis le fichier JSON."""
    if not os.path.exists(chemin_fichier):
        print(
            f"❌ Erreur : Le fichier '{chemin_fichier}' est introuvable."
        )
        return []
    try:
        with open(chemin_fichier, "r", encoding="utf-8") as f:
            structure = json.load(f)
            return structure.get("data", [])
    except Exception as e:
        print(f"❌ Erreur lors de la lecture du fichier : {e}")
        return []


def enregistrer_pannes(liste_pannes, chemin_sortie):
    """Enregistre les sites en panne dans un fichier JSON structuré."""
    if not liste_pannes:
        if os.path.exists(chemin_sortie):
            try:
                os.remove(chemin_sortie)
            except OSError:
                pass
        return

    donnees_sortie = {"total_en_panne": len(liste_pannes), "data": liste_pannes}
    try:
        with open(chemin_sortie, "w", encoding="utf-8") as f:
            json.dump(donnees_sortie, f, indent=2, ensure_ascii=False)
        print(
            f"💾 Liste des pannes exportée avec succès dans : '{chemin_sortie}'"
        )
    except Exception as e:
        print(f"❌ Impossible d'enregistrer le fichier : {e}")


def check_site(site):
    """Teste un site avec un GET partiel, tolérant sur le temps et le SSL."""
    name = site.get("name", "Nom inconnu")
    url = site.get("url")

    if not url:
        return {
            "name": name,
            "url": "URL manquante",
            "status": "Invalide",
            "accessible": False,
            "category": site.get("category", "Inconnue"),
            "description": site.get("description", ""),
        }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3",
    }

    try:
        # On utilise GET + stream=True : on récupère juste la réponse du serveur sans le contenu HTML
        # timeout=15 donne une vraie chance aux serveurs lents d'initier la connexion
        # verify=False évite de marquer en panne un site dont le certificat SSL est mal configuré
        response = requests.get(
            url,
            headers=headers,
            timeout=15,
            allow_redirects=True,
            stream=True,
            verify=False,
        )

        status = response.status_code
        # Un code de succès ou même une redirection/page d'attente (2xx, 3xx ou même 401/403 pour certains serveurs sécurisés)
        # On valide si le serveur a répondu quelque chose de cohérent
        is_ok = 200 <= status < 400 or status in [401, 403]

        return {
            "name": name,
            "url": url,
            "status": (
                f"HTTP {status}"
                if status not in [401, 403]
                else f"HTTP {status} (Protégé)"
            ),
            "accessible": is_ok,
            "category": site.get("category", "Inconnue"),
            "description": site.get("description", ""),
        }

    except requests.exceptions.Timeout:
        return {
            "name": name,
            "url": url,
            "status": "Timeout (> 15s)",
            "accessible": False,
            "category": site.get("category", "Inconnue"),
            "description": site.get("description", ""),
        }
    except requests.exceptions.RequestException as e:
        return {
            "name": name,
            "url": url,
            "status": "Erreur Connexion/DNS",
            "accessible": False,
            "category": site.get("category", "Inconnue"),
            "description": site.get("description", ""),
        }


def main():
    sites = charger_sites(FICHIER_JSON_SOURCE)
    if not sites:
        return

    print(
        f"Démarrage du test robuste pour {len(sites)} sites ('{FICHIER_JSON_SOURCE}')...\n"
    )

    results = []
    # 10 workers au lieu de 15 pour être encore plus doux avec les connexions simultanées
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_site = {
            executor.submit(check_site, site): site for site in sites
        }

        for future in concurrent.futures.as_completed(future_to_site):
            res = future.result()
            results.append(res)

            icon = "✅" if res["accessible"] else "❌"
            print(f"{icon} [{res['status']}] {res['name']} ({res['url']})")

    pannes = []
    for r in results:
        if not r["accessible"]:
            pannes.append(
                {
                    "name": r["name"],
                    "url": r["url"],
                    "description": r["description"],
                    "category": r["category"],
                    "erreur_constatee": r["status"],
                }
            )

    success_count = len(sites) - len(pannes)
    print(f"\n--- Bilan ---")
    print(f"Sites fonctionnels : {success_count} / {len(sites)}")
    print(f"Sites en panne     : {len(pannes)} / {len(sites)}")

    enregistrer_pannes(pannes, FICHIER_JSON_ERREURS)


if __name__ == "__main__":
    main()