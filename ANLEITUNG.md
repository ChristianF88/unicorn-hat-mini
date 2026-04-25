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

## Pong

Klassisches Schlägerspiel gegen KI. Spielerschläger links (grün), KI-Schläger rechts (blau), cyanfarbener Ball prallt dazwischen.

**Steuerung**
| Aktion | Taste |
|---|---|
| Schläger hoch | X |
| Schläger runter | Y |

Ball-Spin: Wer den Ball ausserhalb der Schläger-Mitte trifft, gibt vertikale Geschwindigkeit mit. Mit Schläger-Mitte abfangen neutralisiert.

### Lvl-1
- Ball-Horizontalgeschwindigkeit: 0,5 Zellen/Tick. KI-Schrittintervall: alle 4 Ticks (langsam).
- Sieg: 5 Punkte.

### Lvl-2
- Ball-Horizontalgeschwindigkeit: 0,7 Zellen/Tick. KI-Schrittintervall: alle 2 Ticks (schnell).
- Sieg: 7 Punkte.

**Niederlage**: KI erreicht Punktelimit zuerst (ohne `winning()`-Animation, nur Exit-Prompt).

---

## Flappy

Ein-Tasten-Reflexspiel. Gelber Vogel in Spalte 4 fällt durch Schwerkraft; Tippen auf **A** = Flügelschlag nach oben. Grüne Röhren scrollen von rechts nach links mit vertikaler Lücke. Durchfliegen gibt Punkte; Berührung einer Röhre, der Decke oder des Bodens beendet das Spiel.

**Steuerung**
| Aktion | Taste |
|---|---|
| Flügelschlag | A (kurz) |

Nach dem Tod wird der Punktestand kurz angezeigt, dann der Exit-Prompt. Endlosspiel — keine Siegbedingung.

### Lvl-1
- Lückengrösse: 3 Reihen. Röhren-Scroll: 0,4 Zellen/Tick. Spawn alle 20 Ticks (~1 s).

### Lvl-2
- Lückengrösse: 2 Reihen. Röhren-Scroll: 0,6 Zellen/Tick. Spawn alle 15 Ticks.

---

## Duell (Mash Duel) — 2 Spieler

Tasten-Hammern als Tauziehen für zwei Spieler. **Roter Spieler** bekommt A und B. **Blauer Spieler** bekommt X und Y. Lang-Druck wird gefiltert (damit der globale ABXY-Ausstiegs-Chord nicht zählt).

Nach 3/2/1-Countdown erscheint das Spielfeld. Der Match endet, sobald die Sieg-Bedingung greift; die Farbe des Gewinners blinkt über den ganzen Bildschirm und ein Banner ("R" / "B") erscheint vor dem Exit-Prompt.

> **Hinweis**: Tastenfreigaben werden vom Input-Pipeline ca. 0,17 s gebündelt — das deckelt die effektive Ereignisrate. Jedes Ereignis zählt aber jedes einzelne Tasten-Zeichen innerhalb der Kombination, also wird gleichzeitiges Hämmern auf mehreren Tasten belohnt.

### Lvl-1 — Einzelbalken (AB gegen XY)

Ein bildschirmfüllender Balken. Zellen links der Grenze sind rot, Zellen rechts blau, die Grenze selbst gelb.

- Pro erkannter Kombo: A- und B-Zeichen → rote Drücke; X und Y → blaue Drücke.
- `pressure ∈ [-1, +1]`, startet bei 0. Jeder rote Druck: `+1/30`. Jeder blaue Druck: `-1/30`.
- Grenzspalte = `8 + round(pressure * 8)`.
- Sieg: `pressure` erreicht +1 (Grenze am rechten Rand → rot gewinnt) oder −1 (Grenze am linken Rand → blau gewinnt).

### Lvl-2 — Vier unabhängige Balken

Vier horizontale Balken übereinander, einer pro Taste. Jeder Balken füllt sich von links nach rechts gemäss seiner eigenen Drückzahl.

| Reihe | Balken | Farbe |
|---|---|---|
| 0 | A | rot |
| 1 | X | blau |
| 2, 3 | Trenner (gedimmtes Weiss) | |
| 4 | B | rot |
| 5 | Y | blau |
| 6 | Trenner (gedimmtes Weiss) | |

- Paarungen: A gegen X (oben), B gegen Y (unten). Balken bewegen sich **unabhängig**.
- Jeder Balken füllt `min(16, count * 17 / 25)` Zellen. Der erste Balken, der den rechten Rand erreicht, gewinnt seine Paarung — und entscheidet damit den Gesamt-Match.
- Strategie: Fokus auf beide Tasten verteilen oder auf eine konzentrieren, um den Gegner-Balken in dieser Paarung zu überholen.

### Lvl-3 — Ausdauer (Decay)

Wie Lvl-2 plus passiver Zerfall: jeden Tick zerfällt jede Drückzahl um `0.04`. Etwa 0,8 Zähler/Sek. — ein voller Balken (25) entleert sich in ca. 31 s, wenn man aufhört. Erzwingt dauerhaftes Hämmern.

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
