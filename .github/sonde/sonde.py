"""Sonde temporaire (lot 6) : collecteur d'agendas sur les vrais sites."""
import subprocess
import sys

subprocess.run([sys.executable, "-m", "grille", "--base", "/tmp/sonde.sqlite", "collecter-agendas", "--motifs"])
