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
| tool set hoeindistance 0.1 | Setzt die Entfernung auf 0.1 Meter vor dem die Hacke vor der Pflanze eingefahren wird |
| tool set hoeindistance | Gibt die hoeindistance zurück |
| tool set hoeoutdistance 0.03 | Setzt die Entfernung auf Meter 0.03 Meter nachdem die Hacke nach der Pflanze ausgefahren wird | 
| tool set hoeoutdistance | Gibt die hoeoutdistance zurück |
| tool set hoemaxdistance 2.1 | Setzt die maximale Entfernung auf 2.1 Meter zu einer Pflanze, wird diese Entfernung überschritten, dann geht der Betriebsmode 3 in Störung (wenn man an einer Pflanze vorbei fährt) |
| tool set hoemaxdistance | Gibt die hoemaxdistance zurück |
| tool set steps | Setzt die Anzahl der Motorschritte für die Sähmaschine |
| tool set steps | Gibt die Anzahl der Motorschritte für die Sähmaschine zurück |
| tool set stepshoe | Setzt die Anzahl der Motorschritte für die Hacke |
| tool set stepshoe | Gibt die Anzahl der Motorschritte für die Hacke zurück |
| tool set mode 1 | Setzt den Betriebmode des Feldroboters auf 1 |
| tool set mode | Gibt den aktuelle Betriebmode des Feldroboters zurück |
| tool set seedfile /home/pi/data/webaro/seed.txt | Setzt die Datendatei auf /home/pi/data/webaro/seed.txt |
| tool set seedfile | Gibt die aktuelle Datendatei zurück |
| tool hoe home | Fährt die Hacke in die Home Position |
| tool hoe move | Fährt die Hacke in die nächste Position |
| tool seeder home | Fährt die Sämaschine in die Home Position |
| tool seeder move | Aktiviert die Sämaschine Auswurf ein Saatkorn |
| tool read | Liest Daten aus der Datendatei ein |
| tool write | Schreibt Daten in Datendatei |
| tool clear | Setzt den Seed speicher zurück |
| tool reset | Setzt den Betriebsmode 3 zurück |

### Betriebsmode

| Betriebsmode | Beschreibung |
| ------ | ------------ |
| 0 | Kein Sähnen und kein Hacken |
| 1 | Sähnen, keine Datenaufnahme |
| 2 | Sähnen, Positionen der Pflanzen werden aufgenommen |
| 3 | Hacken |
