#!/bin/bash

echo "🔄 Starte Git Commit & Push..."

# Alles zum Commit vormerken
git add .

# Commit mit Datum + Nachricht
git commit -m "📦 Update: $(date '+%Y-%m-%d %H:%M') – Automatischer Push"

# Hochladen
git push

echo "✅ Push abgeschlossen!"
