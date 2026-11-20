# Mix Gāyatrī + base musicale (versione approvata)

- **Canto:** estratto C4 del pomeriggio del 15 novembre (file `mantra_Claude`, da 1:29,45 a 1:58,85).
  Due ripetizioni complete; la voce sale di un tono: 1ª ≈ 106 Hz, 2ª ≈ 118,7 Hz.
  Il file con le voci NON è nel repository: è sul Mac di Daniele.
- **Base musicale:** `audio-demo/base-musicale-gayatri-v1.mp3` (solo musica, senza voci).
  - 0:00–0:29 una sola nota di bordone continua a 118,7 Hz (+ ottava sotto), sotto il canto;
  - dalle 0:29 il fondo sale di 9 dB e partono le 5 note rapide in Bhūpālī ripetute 3 volte,
    poi Sa acuto e campana.
- **Generare la base:** `python3 audio-demo/sorgenti/base-musicale-gayatri-v1.py base.wav 29.8 0.35`
  (argomenti: file di uscita, istante d'inizio delle corse in secondi, livello del bordone).
- **Mix finale** (base già con il rialzo dopo il canto):

```
ffmpeg -i mantra-C4.mp3 -i audio-demo/base-musicale-gayatri-v1.mp3 -filter_complex \
 "[0:a]aformat=channel_layouts=stereo,apad=pad_dur=15[v];[v][1:a]amix=inputs=2:normalize=0:duration=longest,loudnorm=I=-16:TP=-1.5:LRA=11" \
 -ar 44100 -b:a 256k mix-gayatri.mp3
```
