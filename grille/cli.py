"""Commandes : python -m grille init | verifier-acces | collecter-tv | lister."""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

import requests

from grille import acces, config, db, tv

JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre",
        "novembre", "décembre"]


def _charger_config(dossier: Path) -> config.Configuration | None:
    try:
        conf = config.charger(dossier)
    except config.ErreurConfig as e:
        print(f"ERREUR de configuration : {e}")
        return None
    par_plateforme = Counter(c.plateforme for c in conf.chaines)
    print(
        f"Configuration lue : {len(conf.chaines)} chaînes ("
        + ", ".join(f"{n} {p}" for p, n in sorted(par_plateforme.items()))
        + f"), dont {sum(c.a_confirmer for c in conf.chaines)} à confirmer"
    )
    print(
        f"  {len(conf.candidats)} candidats, {len(conf.partis)} partis, "
        f"{len(conf.mots_cles)} mots-clés, {len(conf.liste_blanche.get('emissions') or [])} émissions en liste blanche"
    )
    for anomalie in conf.anomalies:
        print(f"  ATTENTION {anomalie}")
    return conf


def cmd_init(args: argparse.Namespace) -> int:
    conf = _charger_config(args.config)
    connexion = db.ouvrir(args.base)
    nb = connexion.execute("SELECT COUNT(*) FROM emissions").fetchone()[0]
    connexion.close()
    print(f"Base prête : {args.base} (table emissions, {nb} émission(s))")
    return 0 if conf is not None else 1


def cmd_verifier_acces(args: argparse.Namespace) -> int:
    conf = _charger_config(args.config)
    if conf is None:
        return 1
    resultats = acces.verifier_tout(conf)
    for r in resultats:
        print(f"[{r.etat:^13}] {r.source} : {r.detail}")
    return 1 if any(r.etat == "erreur" for r in resultats) else 0


def afficher_grille(emissions: list[dict]) -> None:
    jour_courant = None
    for e in emissions:
        debut = datetime.fromisoformat(e["debut"])
        if debut.date() != jour_courant:
            jour_courant = debut.date()
            print(f"\n{JOURS[debut.weekday()].capitalize()} {debut.day} {MOIS[debut.month - 1]}")
        invites = f" — avec {', '.join(e['invites'])}" if e["invites"] else ""
        etat = f" [{e['statut']}]" if e["statut"] != "annoncé" else ""
        print(f"  {debut:%H:%M}  {e['chaine']:<20} {e['categorie']:<9} {e['titre']}{invites}{etat}  ({e['filtre']})")


def _horizon() -> tuple[datetime, datetime]:
    maintenant = datetime.now(tv.PARIS)
    fin = datetime.combine(maintenant.date() + timedelta(days=tv.JOURS_AFFICHES), datetime.min.time(), tv.PARIS)
    return maintenant, fin


def cmd_collecter_tv(args: argparse.Namespace) -> int:
    conf = _charger_config(args.config)
    if conf is None:
        return 1
    if args.fichier:
        chemin = args.fichier
        print(f"Guide lu depuis {chemin}")
    else:
        print(f"Téléchargement du guide : {acces.XMLTV_TNT}")
        try:
            chemin = tv.telecharger(requests.Session())
        except requests.RequestException as e:
            print(f"ERREUR : guide télévision inaccessible ({e})")
            return 1
    connexion = db.ouvrir(args.base)
    maintenant, fin = _horizon()
    try:
        rapport = tv.collecter(conf, chemin, connexion, maintenant)
    finally:
        if not args.fichier:
            chemin.unlink(missing_ok=True)
    par_filtre = Counter(e["filtre"] for e in rapport.retenues)
    print(
        f"{rapport.lus} programmes lus sur les chaînes configurées, {rapport.dans_l_horizon} à venir ; "
        f"{len(rapport.retenues)} retenus ({', '.join(f'{n} {f}' for f, n in sorted(par_filtre.items())) or 'aucun'}), "
        f"{rapport.annulees} passés en « annulé »"
    )
    for nom in rapport.chaines_absentes:
        print(f"  ATTENTION chaîne absente du guide : {nom}")
    if args.motifs:
        for e in rapport.retenues:
            print(f"  {e['debut'][:16]}  {e['chaine']:<20} {e['titre'][:60]:<60} ← {e['filtre']} : {e['motif']}")
    emissions = [e for e in db.lister(connexion, maintenant, fin) if e["plateforme"] == "tv"]
    connexion.close()
    print(f"\nÉmissions politiques à la télévision, aujourd'hui et les 7 jours suivants : {len(emissions)}")
    afficher_grille(emissions)
    return 0


def cmd_lister(args: argparse.Namespace) -> int:
    connexion = db.ouvrir(args.base)
    maintenant, fin = _horizon()
    emissions = db.lister(connexion, maintenant, fin)
    connexion.close()
    print(f"Émissions politiques, aujourd'hui et les 7 jours suivants : {len(emissions)}")
    afficher_grille(emissions)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m grille", description="Grille politique Présidentielle 2027")
    parser.add_argument("--config", type=Path, default=config.DOSSIER_CONFIG, help="dossier des fichiers YAML")
    parser.add_argument("--base", type=Path, default=db.CHEMIN_BASE, help="fichier SQLite")
    sous = parser.add_subparsers(dest="commande", required=True)
    sous.add_parser("init", help="crée la base si besoin et lit la configuration").set_defaults(func=cmd_init)
    sous.add_parser("verifier-acces", help="teste le guide XMLTV et les API YouTube et Twitch").set_defaults(
        func=cmd_verifier_acces
    )
    collecte = sous.add_parser("collecter-tv", help="lit le guide XMLTV, garde le politique, écrit en base, affiche")
    collecte.add_argument("--fichier", type=Path, help="guide déjà téléchargé (.xml ou .xml.gz) au lieu de xmltvfr.fr")
    collecte.add_argument("--motifs", action="store_true", help="affiche la règle qui a retenu chaque émission")
    collecte.set_defaults(func=cmd_collecter_tv)
    sous.add_parser("lister", help="affiche la grille enregistrée en base").set_defaults(func=cmd_lister)
    args = parser.parse_args(argv)
    return args.func(args)
