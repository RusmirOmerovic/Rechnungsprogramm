#!/bin/bash

# Skript zur automatischen Vorbereitung der Entwicklungsumgebung

echo "🔧 Deaktiviere bestehende virtuelle Umgebung (falls aktiv)..."
deactivate 2>/dev/null

echo "🧹 Lösche alte virtuelle Umgebung..."
rm -rf .venv

echo "🐍 Erstelle neue virtuelle Umgebung..."
python3 -m venv .venv

echo "⚡ Aktiviere neue virtuelle Umgebung..."
source .venv/bin/activate

echo "⬆️ Aktualisiere pip..."
pip install --upgrade pip

echo "📦 Installiere benötigte Pakete..."
pip install fpdf2 Pillow

echo "📝 Speichere Abhängigkeiten in requirements.txt..."
pip freeze > requirements.txt

echo "✅ Setup abgeschlossen! Starte dein Programm mit: ./start.sh"
