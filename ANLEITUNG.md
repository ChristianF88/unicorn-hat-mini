# Unicorn HAT Mini — Spielanleitung (DE)

Sammlung kleiner Spiele auf einer 17×7-LED-Matrix mit vier Tasten (A, B, X, Y).

## Globale Steuerung

| Aktion | Tasten |
|---|---|
| Menü: hoch | X (kurz) |
| Menü: runter | Y (kurz) |
| Menü: bestätigen | A (kurz) |
| Menü: zurück | B (kurz) |
| Spiel beenden | A + B + X + Y lang drücken (> 1,1 s) |

"Lang drücken" bedeutet immer halten > 1,1 s. "Kombo" bedeutet mehrere Tasten gleichzeitig drücken (innerhalb von ca. 0,17 s loslassen).

---

## Labyrinth

Bewege den Spielerpunkt vom linken Eingang zum rechten Ausgang durch das generierte Labyrinth. Die Ansicht scrollt mit dem Spieler.

**Level**: 1 – 15. Labyrinthgröße wächst mit `(10·N + 1) × (10·N + 1)` Zellen. Höheres Level = grösseres Labyrinth.

**Steuerung**
| Aktion | Taste |
|---|---|
| Nach links | A |
| Nach rechts | B |
| Nach oben | X |
| Nach unten | Y |
| Auto-Lösung (Aufgeben) | A + B + X lang |

**Ziel**: Ausgang erreichen. Auto-Lösung animiert den BFS-Pfad und beendet das Spiel.

---

## Reaktion

Sieben Schwierigkeitsstufen. Pro Level: 15 erfolgreiche Runden für Sieg, 3 Leben, Reaktionszeit wird nach jedem Treffer angezeigt.

### Lvl-1 — Grundreaktion
Eine Ecke blinkt rot. Drücke die passende Taste.
- Reaktionszeit: 0,5 s nach Blinken. Langsamer = Leben verloren.
- Kein Anzeige-Timeout — das Spiel wartet auf den Tastendruck.

### Lvl-2 — Farbfilter
Eine Ecke blinkt **rot oder blau**.
- Drücke die Taste **nur bei Rot**. Bei Blau: nichts tun (1 s Anzeige-Timeout, Runde besteht).
- Druck bei Blau oder falsche Taste = Leben verloren.

### Lvl-3 — Kombo-Druck
Zwei Ecken blinken gleichzeitig rot (z. B. A + X).
- Drücke beide Tasten gleichzeitig. Reaktionszeit 0,7 s.
- Falsche Kombo oder Einzeldruck = Leben verloren.

### Lvl-4 — Köder (einfach)
3 von 4 Ecken blinken in Zufallsfarben {rot, grün, blau}; **genau eine ist rot**.
- Drücke die rote Ecke. Anzeige-Timeout 1,2 s.
- Falsche Ecke / Timeout = Leben verloren. Reaktionsfenster 0,5 s.

### Lvl-5 — Köder (mehrfach)
Alle 4 Ecken blinken. **1 oder 2 sind rot**, der Rest grün/blau.
- Drücke die Kombo der roten Ecken (z. B. rot bei A und X → A + X drücken).
- Anzeige-Timeout 1,5 s, Reaktionsfenster 0,8 s.

### Lvl-6 — Simon (feste Sequenzen)
Eine Sequenz aus N Tasten blinkt rot, dann "R" (Ready), Pause, "G" (Go). Wiederhole die Sequenz.
- Runde 1 = Länge 1 → Runde 15 = Länge 15.
- Eingabefenster pro Taste: 0,75 s.
- Bei Fehler (falsche Taste oder Timeout): 1 Leben verloren, **gleiche Länge** wird mit anderer Sequenz wiederholt (3 deterministische Sequenzen pro Länge).
- Sequenzen sind vorgegeben (immer gleich bei jedem Spielstart).

### Lvl-7 — Simon (zufällige Sequenzen)
Gleicher Ablauf wie Lvl-6, aber Sequenzen werden bei jedem Spiel neu zufällig gewürfelt.

---

## Space (Weltraum-Shooter)

Seitwärts scrollender Shooter. Schiff links, Meteoriten kommen von rechts. Treffe sie, bevor sie dich treffen.

**Steuerung**
| Aktion | Taste |
|---|---|
| Schiff hoch | X |
| Schiff runter | Y |
| Schiessen | A |

**Leben**: 3. Nach Treffer blinkt das Schiff (Unverwundbarkeit ca. 1 s).

### Lvl-1
- Spawn-Intervall: 15 Ticks (langsam). Meteorgeschwindigkeit: langsam. Max. 1 Meteor pro Spawn.
- Sieg: 30 Treffer.
- Schwierigkeit steigt bei Punkten 8 / 15 / 25.

### Lvl-2
- Spawn-Intervall: 10 Ticks. Meteorgeschwindigkeit: schneller. Bis zu 3 Meteoren pro Spawn.
- Sieg: 50 Treffer.
- Schwierigkeit steigt bei Punkten 8 / 15 / 25 / 40.

---

## Game of Life

Conways "Game of Life" auf einem 17×7-Torus-Gitter (Ränder wrappen). Drei Untermodi: **Editor**, **Preset-Auswahl**, **Simulation**.

### Editor-Modus (Standard beim Start)

Bewege den Cursor (blau), schalte Zellen ein/aus (grün = lebendig), starte dann die Simulation.

| Aktion | Taste |
|---|---|
| Cursor links | A (kurz) |
| Cursor rechts | B (kurz) |
| Cursor hoch | X (kurz) |
| Cursor runter | Y (kurz) |
| Zelle am Cursor umschalten | A + X (Kombo) |
| Simulation starten | B + Y (Kombo) |
| **Gitter leeren** | A (lang) |
| **Gitter zufällig füllen** | B (lang) |
| **Preset-Auswahl öffnen** | X (lang) |

Ein kurzes Banner ("C" / "?" / "P" / "R") erscheint bei jeder Aktion / jedem Moduswechsel.

### Preset-Auswahl-Modus

Vordefinierte Muster durchblättern und am Cursor platzieren. Vorschau in **gelb** über dem Gitter; Überlappung mit lebendigen Zellen erscheint **orange**. Cursor bleibt fixiert — vorher im Editor positionieren.

| Aktion | Taste |
|---|---|
| Vorheriges Preset | X (kurz) |
| Nächstes Preset | Y (kurz) |
| Drop-Modus wechseln (OR / XOR / REPLACE) | X + Y (Kombo) |
| Platzierung am Cursor bestätigen | A (kurz) |
| Abbrechen, zurück zum Editor | B (kurz) |

**Drop-Modi**:
- **OR** — Preset-Zellen werden eingeschaltet; bestehende Zellen unverändert.
- **XOR** — Preset-Zellen umschalten (tötet überlappende lebendige Zellen, schaltet leere ein).
- **REPLACE** — Gitter leeren, dann Preset platzieren.

Verfügbare Presets: Glider, R-Pentomino, Lightweight Spaceship, Blinker, Block, Pulsar-Fragment.

### Simulations-Modus

Zellen folgen Conways Regeln. Geschwindigkeit und Pause in Echtzeit anpassbar.

| Aktion | Taste |
|---|---|
| Pause / Fortsetzen | A (kurz) |
| Langsamer (längerer Schritt) | X (kurz) |
| Schneller (kürzerer Schritt) | Y (kurz) |
| Zurück zum Editor (laufend) | B (kurz) |
| **Einen Schritt vor** (in Pause) | B (kurz) |
| Zurück zum Editor (immer) | B (lang) |
| Während der Simulation zufällig füllen | Y (lang) |

Lebendige Zellen: grün (laufend) / orange (pausiert).

---

## Hinweise

- "Kombo" bedeutet, dass Tasten innerhalb von ca. 0,17 s gemeinsam losgelassen werden.
- "Lang drücken" Schwelle: 1,1 s.
- Universaler Ausstieg (jedes Spiel): A + B + X + Y > 1,1 s halten.
