"""Commandes : python -m grille init | verifier-acces."""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

from grille import acces, config, db


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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m grille", description="Grille politique Présidentielle 2027")
    parser.add_argument("--config", type=Path, default=config.DOSSIER_CONFIG, help="dossier des fichiers YAML")
    parser.add_argument("--base", type=Path, default=db.CHEMIN_BASE, help="fichier SQLite")
    sous = parser.add_subparsers(dest="commande", required=True)
    sous.add_parser("init", help="crée la base si besoin et lit la configuration").set_defaults(func=cmd_init)
    sous.add_parser("verifier-acces", help="teste le guide XMLTV et les API YouTube et Twitch").set_defaults(
        func=cmd_verifier_acces
    )
    args = parser.parse_args(argv)
    return args.func(args)
