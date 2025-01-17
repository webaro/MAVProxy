# Befehle

## NTRIP

| Befehl | Beschreibung |
| ------ | ------------ |
| ntrip set caster openservice-sapos.niedersachsen.de | Setzt den NTRIP Caster auf openservice-sapos.niedersachsen.de |
| ntrip set caster | Gibt den aktullen NTRIP Caster zurück |
| ntrip set mountpoint VRS_3_3G_NI | Setzt den NTRIP mountpoint auf VRS_3_3G_NI |
| ntrip set mountpoint | Gibt den aktuellen NTRIP Mountpoint zurück |
| ntrip set password test | Setzt das NTRIP Passwort auf test |
| ntrip set password | Gibt das aktuelle NTRIP Passwort zurück |
| ntrip set port 2101 | Setzt den NTRIP Port auf 2101 |
| ntrip set port | Gibt den aktuellen NTRIP Port zurück |
| ntrip set username test | Setzt den NTRIP Benutzernamen auf test |
| ntrip set username | Gibt den aktuellen NTRIP Benutzernamen zurück |
| ntrip stop | Stoppt den NTRIP Service |
| ntrip start | Startet den NTRIP Service |

## FELDROBOTER

![](docs/seedhoe.drawio.png)

| Befehl | Beschreibung |
| ------ | ------------ |
| `tool set hoe_indistance 0.1` | Setzt die Entfernung auf 0.1 Meter vor dem die Hacke vor der Pflanze eingefahren wird |
| `tool set hoe_indistance` | Gibt die hoeindistance zurück |
| `tool set hoe_outdistance 0.03` | Setzt die Entfernung auf Meter 0.03 Meter nachdem die Hacke nach der Pflanze ausgefahren wird | 
| `tool set hoe_outdistance` | Gibt die hoeoutdistance zurück |
| `tool set hoe_maxdistance 2.1` | Setzt die maximale Entfernung auf 2.1 Meter zu einer Pflanze, wird diese Entfernung überschritten, dann geht der Betriebsmode 3 in Störung (wenn man an einer Pflanze vorbei fährt) |
| `tool set hoe_maxdistance` | Gibt die hoemaxdistance zurück |
| `tool set hoe_steps 200` | Setzt die Anzahl der Motorschritte für die Hacke auf 200 |
| `tool set hoe_steps` | Gibt die Anzahl der Motorschritte für die Hacke zurück |
| `tool set seeder_steps 200` | Setzt die Anzahl der Motorschritte für die Sähmaschine auf 200 |
| `tool set seeder_steps` | Gibt die Anzahl der Motorschritte für die Sähmaschine zurück |
| `tool set mode 1` | Setzt den Betriebmode des Feldroboters auf 1 |
| `tool set mode` | Gibt den aktuelle Betriebmode des Feldroboters zurück |
| `tool set seedfile /home/pi/data/webaro/seed.txt` | Setzt die Datendatei auf /home/pi/data/webaro/seed.txt |
| `tool set seedfile` | Gibt die aktuelle Datendatei zurück |
| `tool hoe home` | Fährt die Hacke in die Home Position |
| `tool hoe move` | Fährt die Hacke in die nächste Position |
| `tool hoe start` | Öffnet Datenfile und beginnt mit dem Haken |
| `tool hoe stop` | Beendet das Haken |
| `tool seeder home` | Fährt die Sämaschine in die Home Position |
| `tool seeder move` | Aktiviert die Sämaschine Auswurf ein Saatkorn |
| `tool seeder start` | Erstellt Datenfile und beginnt mit dem Säen und der Datenaufnahme |
| `tool seeder stop` | Schließt Datenfile und beendet das Säen und die Datenaufnahme |
| `tool read` | Liest Daten aus der Datendatei ein |
| `tool write` | Schreibt Daten in Datendatei |
| `tool clear` | Setzt den Seed speicher zurück |
| `tool reset` | Setzt den Betriebsmode zurück |

### Betriebsmode

| Betriebsmode | Beschreibung |
| ------ | ------------ |
| 0 | Kein Sähnen und kein Hacken |
| 1 | Sähnen, keine Datenaufnahme |
| 2 | Sähnen, Positionen der Pflanzen werden aufgenommen |
| 3 | Hacken |

### Verfahren zum Aussäen und Positionen speichern
File für Daten setzen: `tool set seed file /home/pi/data/webaro/seed.txt`

Datenaufnahme starten: `tool seeder start`

Nach dem Ende der Mission Datenaufnahme stoppen: `tool seeder stop`

### Verfahren zum Haken
File für Daten setzen: `tool set seed file /home/pi/data/webaro/seed.txt`

Haken starten: `tool hoe start`

Nach dem Ende der Mission das Haken stoppen: `tool hoe stop`