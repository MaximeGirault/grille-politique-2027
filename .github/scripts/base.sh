#!/usr/bin/env bash
# Base SQLite conservée sur la branche « donnees », qui ne garde que la dernière version :
# chaque enregistrement remplace le précédent, l'historique du dépôt ne grossit pas.
#   base.sh recuperer   → data/grille.sqlite (base neuve si la branche n'existe pas encore)
#   base.sh enregistrer → remplace le contenu de la branche par data/grille.sqlite
# DEPOT_DISTANT permet de tester le script avec un dépôt local.
set -euo pipefail
mkdir -p data

case "${1:-}" in
  recuperer)
    if git fetch --quiet --depth=1 origin donnees 2>/dev/null; then
      git show FETCH_HEAD:grille.sqlite > data/grille.sqlite
      echo "Base récupérée ($(du -h data/grille.sqlite | cut -f1))"
    else
      echo "Branche donnees absente : première exécution, base neuve"
    fi
    ;;
  enregistrer)
    dossier=$(mktemp -d)
    cp data/grille.sqlite "$dossier/"
    cat > "$dossier/LISEZMOI.md" <<'TEXTE'
Base de la grille, mise à jour par les tâches GitHub (collecte horaire, email du matin).
Cette branche ne garde que la dernière version : ne pas y travailler.
TEXTE
    cd "$dossier"
    git init --quiet --initial-branch=donnees
    git add grille.sqlite LISEZMOI.md
    git -c user.name="github-actions[bot]" -c user.email="41898282+github-actions[bot]@users.noreply.github.com" \
      commit --quiet -m "Base du $(TZ=Europe/Paris date '+%d/%m/%Y à %H:%M')"
    git push --quiet --force "${DEPOT_DISTANT:-https://x-access-token:${GITHUB_TOKEN}@github.com/${GITHUB_REPOSITORY}.git}" donnees
    echo "Base enregistrée sur la branche donnees"
    ;;
  *)
    echo "usage : $0 recuperer|enregistrer" >&2
    exit 2
    ;;
esac
