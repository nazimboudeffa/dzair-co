import concurrent.futures
import json
import os
import requests

# Chemins des fichiers
FICHIER_JSON_SOURCE = "sites.json"
FICHIER_JSON_ERREURS = "sites_en_panne.json"


def charger_sites(chemin_fichier):
    """Charge la liste des sites depuis le fichier JSON."""
    if not os.path.exists(chemin_fichier):
        print(
            f"❌ Erreur : Le fichier '{chemin_fichier}' est introuvable. "
            "Vérifiez qu'il est bien dans le même dossier que le script."
        )
        return []

    try:
        with open(chemin_fichier, "r", encoding="utf-8") as f:
            structure = json.load(f)
            return structure.get("data", [])
    except json.JSONDecodeError:
        print(
            f"❌ Erreur : Le fichier '{chemin_fichier}' n'est pas un JSON valide."
        )
        return []
    except Exception as e:
        print(f"❌ Erreur lors de la lecture du fichier : {e}")
        return []


def enregistrer_pannes(liste_pannes, chemin_sortie):
    """Enregistre les sites en panne dans un fichier JSON structuré."""
    if not liste_pannes:
        # Si le fichier de pannes précédent existe, on le nettoie car tout est OK désormais
        if os.path.exists(chemin_sortie):
            try:
                os.remove(chemin_sortie)
            except OSError:
                pass
        return

    # Optionnel : On réintègre les descriptions et catégories d'origine si disponibles
    donnees_sortie = {"total_en_panne": len(liste_pannes), "data": liste_pannes}

    try:
        with open(chemin_sortie, "w", encoding="utf-8") as f:
            json.dump(donnees_sortie, f, indent=2, ensure_ascii=False)
        print(
            f"💾 Liste des pannes exportée avec succès dans : '{chemin_sortie}'"
        )
    except Exception as e:
        print(
            f"❌ Impossible d'enregistrer le fichier de pannes ({chemin_sortie}) : {e}"
        )


def check_site(site):
    """Teste un site unique avec une requête HEAD non intrusive."""
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
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        # Requête HEAD (rapide, légère et discrète)
        response = requests.head(
            url, headers=headers, timeout=5, allow_redirects=True
        )

        # Si HEAD est rejeté (403/405/501), on tente un micro GET
        if response.status_code in [403, 405, 501]:
            response = requests.get(
                url, headers=headers, timeout=5, allow_redirects=True, stream=True
            )

        status = response.status_code
        is_ok = 200 <= status < 400

        return {
            "name": name,
            "url": url,
            "status": status,
            "accessible": is_ok,
            "category": site.get("category", "Inconnue"),
            "description": site.get("description", ""),
        }

    except requests.exceptions.RequestException:
        return {
            "name": name,
            "url": url,
            "status": "Hors ligne / Timeout",
            "accessible": False,
            "category": site.get("category", "Inconnue"),
            "description": site.get("description", ""),
        }


def main():
    # 1. Chargement des données d'origine
    sites = charger_sites(FICHIER_JSON_SOURCE)

    if not sites:
        print("Fin du script (aucune donnée à traiter).")
        return

    print(
        f"Démarrage du test pour {len(sites)} sites issus de '{FICHIER_JSON_SOURCE}'...\n"
    )

    # 2. Analyse parallélisée
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
        future_to_site = {
            executor.submit(check_site, site): site for site in sites
        }

        for future in concurrent.futures.as_completed(future_to_site):
            res = future.result()
            results.append(res)

            # Affichage console en direct
            icon = "✅" if res["accessible"] else "❌"
            print(f"{icon} [{res['status']}] {res['name']} ({res['url']})")

    # 3. Filtrage et tri des erreurs
    pannes = []
    for r in results:
        if not r["accessible"]:
            # On construit l'objet de panne en gardant la structure d'origine + la raison
            pannes.append(
                {
                    "name": r["name"],
                    "url": r["url"],
                    "description": r["description"],
                    "category": r["category"],
                    "erreur_constatee": str(r["status"]),
                }
            )

    # 4. Bilan final et écriture du fichier à part
    success_count = len(sites) - len(pannes)
    print(f"\n--- Bilan ---")
    print(f"Sites fonctionnels : {success_count} / {len(sites)}")
    print(f"Sites en panne     : {len(pannes)} / {len(sites)}")

    enregistrer_pannes(pannes, FICHIER_JSON_ERREURS)


if __name__ == "__main__":
    main()