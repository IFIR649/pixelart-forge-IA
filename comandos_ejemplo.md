** COMANDO QUE USO CLAUDE **

´´´
$ curl -s http://localhost:3000/poll 2>&1 | head -50
{"commands": []}
Servidor activo. Enviando la entidad cósmica en tres batches: base/tentáculos, cuerpo/núcleo, ojos/detalles.


Ejecutado 4 comandos
Ejecutó
Batch 1: setup, ambient rings, 8 tentacles in 4 stroke layers
Bash
$ curl -s -X POST http://localhost:3000/batch \
  -H "Content-Type: application/json" \
  -d '{
  "commands": [
    "setsize 64",
    "setbg #000000",
    "clear",
    "stroke 2",
    "circle 32 32 31 #060014",
    "circle 32 32 29 #0a001e",
    "circle 32 32 27 #0d0026",
    "stroke 7",
    "curve 32 17 23 7 26 1 #0c001a",
    "curve 44 21 55 13 62 3 #0c001a",
    "curve 47 32 58 26 63 30 #0c001a",
    "curve 44 43 55 52 62 62 #0c001a",
    "curve 32 47 38 57 34 63 #0c001a",
    "curve 20 43 9 53 2 62 #0c001a",
    "curve 17 32 6 37 1 30 #0c001a",
    "curve 20 21 9 11 2 3 #0c001a",
    "stroke 5",
    "curve 32 17 23 7 26 1 #1c0040",
    "curve 44 21 55 13 62 3 #1c0040",
    "curve 47 32 58 26 63 30 #1c0040",
    "curve 44 43 55 52 62 62 #1c0040",
    "curve 32 47 38 57 34 63 #1c0040",
    "curve 20 43 9 53 2 62 #1c0040",
    "curve 17 32 6 37 1 30 #1c0040",
    "curve 20 21 9 11 2 3 #1c0040",
    "stroke 3",
    "curve 32 17 23 7 26 1 #4400aa",
    "curve 44 21 55 13 62 3 #4400aa",
    "curve 47 32 58 26 63 30 #4400aa",
    "curve 44 43 55 52 62 62 #4400aa",
    "curve 32 47 38 57 34 63 #4400aa",
    "curve 20 43 9 53 2 62 #4400aa",
    "curve 17 32 6 37 1 30 #4400aa",
    "curve 20 21 9 11 2 3 #4400aa",
    "stroke 1",
    "curve 32 17 23 7 26 1 #8833dd",
    "curve 44 21 55 13 62 3 #8833dd",
    "curve 47 32 58 26 63 30 #8833dd",
    "curve 44 43 55 52 62 62 #8833dd",
    "curve 32 47 38 57 34 63 #8833dd",
    "curve 20 43 9 53 2 62 #8833dd",
    "curve 17 32 6 37 1 30 #8833dd",
    "curve 20 21 9 11 2 3 #8833dd"
  ]
}'
{"ok": true, "count": 43, "queued": 43}
Ejecutó
Batch 2: body blob, energy rings, glowing core, energy spikes
Bash
$ sleep 2 && curl -s -X POST http://localhost:3000/batch \
  -H "Content-Type: application/json" \
  -d '{
  "commands": [
    "fillcircle 32 32 18 #080018",
    "fillcircle 28 30 13 #0e0025",
    "fillcircle 36 29 11 #0e0025",
    "fillcircle 30 36 10 #0e0025",
    "fillcircle 32 31 15 #140033",
    "fillcircle 32 31 13 #1c0045",
    "fillcircle 32 31 11 #250055",
    "fillcircle 32 30 9 #300068",
    "stroke 2",
    "circle 32 31 14 #400080",
    "circle 32 30 12 #5500aa",
    "stroke 1",
    "circle 32 30 10 #6600cc",
    "circle 32 30 8 #7711dd",
    "circle 32 30 6 #8833ee",
    "fillcircle 32 30 5 #9944ee",
    "fillcircle 32 30 4 #bb66ff",
    "fillcircle 32 30 3 #dd99ff",
    "fillcircle 32 30 2 #eeccff",
    "dot 32 30 1 #ffffff",
    "stroke 1",
    "drawline 32 30 32 22 #cc88ff",
    "drawline 32 30 32 38 #cc88ff",
    "drawline 32 30 24 30 #cc88ff",
    "drawline 32 30 40 30 #cc88ff",
    "drawline 32 30 26 24 #cc88ff",
    "drawline 32 30 38 36 #cc88ff",
    "drawline 32 30 38 24 #cc88ff",
    "drawline 32 30 26 36 #cc88ff",
    "dot 32 30 1 #ffffff"
  ]
}'
{"ok": true, "count": 30, "queued": 30}
Ejecutó
Batch 3: three eyes, star particles, tentacle tip glows, outer cosmic ring, snapshot
Bash
$ sleep 2 && curl -s -X POST http://localhost:3000/batch \
  -H "Content-Type: application/json" \
  -d '{
  "commands": [
    "fillcircle 27 27 4 #1a0005",
    "fillcircle 37 27 4 #1a0005",
    "fillcircle 32 23 3 #1a0005",
    "fillcircle 27 27 3 #aa0020",
    "fillcircle 37 27 3 #aa0020",
    "fillcircle 32 23 2 #aa0020",
    "stroke 1",
    "circle 27 27 3 #ff2244",
    "circle 37 27 3 #ff2244",
    "circle 32 23 2 #ff2244",
    "dot 27 27 1 #ff88aa",
    "dot 37 27 1 #ff88aa",
    "dot 32 23 1 #ff88aa",
    "drawline 27 25 27 29 #000000",
    "drawline 37 25 37 29 #000000",
    "dot 5 8 1 #aaaaff",
    "dot 59 6 1 #ffffff",
    "dot 3 21 1 #ffaaff",
    "dot 61 20 1 #aaaaff",
    "dot 62 44 1 #ffffff",
    "dot 2 45 1 #aaaaff",
    "dot 9 58 1 #ffffff",
    "dot 55 60 1 #ffaaff",
    "dot 1 32 1 #ffffff",
    "dot 62 32 1 #aaaaff",
    "dot 13 3 1 #ffffff",
    "dot 50 2 1 #ffaaff",
    "dot 7 15 1 #ffffff",
    "dot 57 14 1 #aaaaff",
    "dot 26 1 2 #7722cc",
    "dot 62 3 2 #7722cc",
    "dot 63 30 2 #7722cc",
    "dot 62 62 2 #7722cc",
    "dot 34 63 2 #7722cc",
    "dot 2 62 2 #7722cc",
    "dot 1 30 2 #7722cc",
    "dot 2 3 2 #7722cc",
    "stroke 1",
    "circle 32 32 31 #110022",
    "circle 32 32 29 #1a0033",
    "snapshot cosmic_entity 8"
  ]
}'
{"ok": true, "count": 41, "queued": 41}
Ejecutó
Check that snapshot was saved
Bash
$ sleep 3 && ls "C:\Users\Alexis\Documents\alex\proyectos_personales_rapidos\pixel-art-charge\snapshots" | grep cosmic
cosmic_entity.json
cosmic_entity.png
´´´