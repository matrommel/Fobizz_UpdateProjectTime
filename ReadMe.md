## Idee
In Fobizz können für Gruppen Projekte angelegt werden. Diese Projekte sind maximal 6 Tage gültig und müssen per Klick auf Button verlängert werden. Dieses Skript aktualisiert alle Projekte aller Klassen auf den maximalen Zeitraum.

### Anleitung
1. Erstelle config.ini Datei mit folgendem Inhalt
<pre>
[login]
username = Hello
password = World
</pre>

2. Führe init.py aus
<pre>
$ python init.py
</pre>

### Optional unter Windows 
Erstelle eine run.cmd mit folgenden inhalt
<pre>
@echo off  <br>
python ./init.py
pause
</pre>