# Playlistr

Ein TUI zum automatischen Erstellen und Erweitern von Spotify-Playlists nach Artist – z.B. "füge mir alle Songs (inklusive Features), die ich von Artist X geliked oder in eigenen Playlists liegen habe, zu einer bestehenden oder neuen Playlist hinzu."

## Features

- TUI-Auswahl statt hardcodierter Artist-Namen im Code, mit Autovervollständigung – Vorschläge basieren auf deiner eigenen Bibliothek, sortiert nach Häufigkeit
- Findet auch Tracks, auf denen der Artist nur als Feature auftaucht, nicht nur Hauptkünstler
- Ziel-Playlist frei auswählbar oder direkt neu anlegen
- Prüft vor dem Hinzufügen, ob ein Song schon in der Playlist ist – keine Duplikate
- Lokaler Cache deiner Bibliothek (Liked Songs + eigene Playlists), damit nicht bei jedem Start alles neu von der Spotify-API geladen wird

## Voraussetzungen

- Python 3.14+
- [uv](https://docs.astral.sh/uv/)
- Ein Spotify-Account – **Premium ist nicht nötig**, das Tool spielt nichts ab, es liest/schreibt nur Bibliothek und Playlists

## Installation

```bash
uv sync
```

## Erster Start

Playlistr nutzt eine gemeinsame Spotify-App (PKCE-Flow, kein Secret nötig – die `client_id` steckt direkt im Code). Diese App läuft im "Development Mode" von Spotify, daher müssen neue Nutzer manuell freigeschaltet werden: melde dich beim Projektinhaber mit der E-Mail-Adresse deines Spotify-Accounts, damit du hinzugefügt werden kannst.

Danach:

```bash
uv run playlistr
```

Beim ersten Start öffnet sich dein Browser für den Spotify-Login. Der Token wird anschließend lokal in `.cache` gespeichert – du musst dich nicht bei jedem Start neu einloggen.

## Nutzung

1. Artist eingeben (mit Autovervollständigung)
2. Songs auswählen, die hinzugefügt werden sollen
3. Ziel-Playlist wählen oder neu anlegen
4. Fertig – bereits vorhandene Songs werden automatisch übersprungen

Danach kannst du direkt mit dem nächsten Artist weitermachen. Mit `Strg+C` jederzeit sauber beenden.

## Wie der Cache funktioniert

Beim ersten Aufruf lädt Playlistr deine komplette Bibliothek (Liked Songs + Tracks aus allen eigenen Playlists) und speichert sie für eine Stunde lokal in `song_cache.json` zwischen (landet nicht in Git, siehe `.gitignore`). Das reduziert die Spotify-API-Calls drastisch – ohne den Cache läuft man schnell in ein Rate-Limit, besonders wenn mehrere Leute dieselbe App gleichzeitig nutzen. Willst du frische Daten erzwingen, lösch einfach `song_cache.json`.

**Hinweis:** Es werden nur Playlists berücksichtigt, deren Owner du selbst bist – gefolgte oder kollaborative Playlists anderer Leute fließen aktuell nicht mit ein.

## Projektstruktur

```
src/playlistr/
├── __init__.py   # Einstiegspunkt (main-Loop)
├── tui.py        # Interaktive Prompts (questionary)
├── spotify.py    # Spotify-API-Zugriff & Caching
└── helper.py     # kleine Hilfsfunktionen

docs/
└── datenstrukturen-tutorial.md   # Python-Datenstrukturen-Guide
```

## Bekannte Einschränkungen

- Development-Mode-App: maximal 5 freigeschaltete Spotify-Accounts gleichzeitig
- Es werden nur eigene Playlists durchsucht, keine gefolgten/kollaborativen fremder Owner

## ToDos
- Artists richtig finden -> Es werden nicht immer alle Songs der Artists angezeigt
