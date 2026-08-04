# -*- coding: utf-8 -*-
"""Pone en sw.js una VERSION derivada del contenido real de la app.

POR QUE EXISTE. La version de la cache habia que subirla a mano en cada
despliegue, con un aviso en mayusculas en el propio fichero. Se olvido seis
veces seguidas -incluido por quien escribio el aviso-, y el sintoma es que el
movil sigue mostrando la version anterior. Un recordatorio que se ignora seis
veces no es un recordatorio: es un paso que tiene que hacer la maquina.

    python sellar_sw.py     # antes de cada commit que toque la app
"""
import hashlib, io, os, re, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
SW   = os.path.join(AQUI, 'sw.js')
# Todo lo que se precachea entra en el hash: si cambia cualquiera, cambia la version.
FUENTES = ['index.html', 'manifest.webmanifest',
           'iconos/icono-192.png', 'iconos/icono-512.png']

h = hashlib.sha256()
for f in FUENTES:
    p = os.path.join(AQUI, f)
    if os.path.exists(p):
        h.update(open(p, 'rb').read())
sello = h.hexdigest()[:12]

s = io.open(SW, 'rb').read().decode('utf-8').replace('\r\n', '\n')
nueva = "const VERSION = 'atlas-%s';" % sello
s2, n = re.subn(r"const VERSION = '[^']+';", nueva, s, count=1)
if not n:
    print('no encuentro la linea de VERSION en sw.js'); sys.exit(1)
if s2 == s:
    print('sin cambios: la version ya es atlas-%s' % sello); sys.exit(0)
io.open(SW, 'wb').write(s2.replace('\n', '\r\n').encode('utf-8'))
print('VERSION -> atlas-%s' % sello)
