# Regénérer la vidéo de présentation

Outils (pour développeur, Linux avec Node + Playwright + ffmpeg) :

1. Vidéo source de démo :
   `ffmpeg -f lavfi -i "nullsrc=s=640x360:r=30:d=20,geq=r='128+110*sin(X/45+T*1.7)':g='128+110*sin(Y/28-T*1.2)':b='128+110*sin((X+Y)/60+T*0.8)'" -c:v libvpx -b:v 2M plasma.webm`
   (à placer à côté de `record.js`)
2. Faux relais (répond sans envoyer d'UDP) : `python3 fake_bridge.py ../..` (port 8090)
3. Enregistrement : `node record.js` → `rec/*.webm`
4. Conversion : `ffmpeg -ss 0.4 -i rec/page@*.webm -c:v libx264 -crf 22 -pix_fmt yuv420p -movflags +faststart ../presentation.mp4`
