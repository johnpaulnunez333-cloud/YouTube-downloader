🎥 YouTube Downloader (Web App)

Isang responsive web application na binuo upang magsilbing tool sa pag-download ng mga video mula sa YouTube. Ang proyektong ito ay nakatuon sa pagproseso ng mga MP4 formats at maayos na UI handling.

🚀 Live Demo
👉 https://you-tube-downloader-iota.vercel.app/
*(Nakuha ko ito sa active deployment tab sa kanan ng iyong repository)*

🧠 Ang Kwento sa Likod ng Pagbuo (Debugging Challenge)
Ang proyektong ito ay nagbigay sa akin ng malaking karanasan sa pag-debug:
- Naglaan ako ng **2 oras sa pag-debug** nang subukan kong mag-integrate ng isang libreng YouTube Downloader API na sa kasamaang palad ay hindi gumana nang maayos.
- Sa halip na huminto, nag-focus ako sa pag-optimize ng frontend logic (`script.js`), pag-aayos ng MP4 format handling, at pagpapalakas ng error handling sa backend (`server.py`).
- Kasalukuyang naka-hold ang external API integration habang naghahanap pa ng mas matatag at stable na libreng alternatibo.

✨ Mga Tampok (Features)
- **Format Handling:** Pinahusay na lohika para sa pag-detect ng tamang MP4 video formats.
- **Robust Error Handling:** Nilagyan ng mas pinagandang backend catch mechanisms sa `server.py` para maiwasan ang biglaang pag-crash ng app.
- **Vercel Optimized:** Naka-configure gamit ang `vercel.json` para sa mabilis at swabe na static/serverless deployment.

 🛠️ Tech Stack
- **Backend:** Python (Flask / Server logic) + Gunicorn
- **Frontend:** HTML5 (26.2%), CSS3 (26.9%), JavaScript (23.3%)
- **Hosting/Deployment:** Vercel

📁 Estruktura ng Repository
- `server.py` - Pangunahing backend code para sa mga API request at routing.
- `script.js` - Nagpapatakbo ng frontend interactions at event listeners.
- `style.css` - Custom styles para sa malinis na interface ng downloader.
- `vercel.json` - Configuration file para sa deployment sa Vercel.

---
*Binuo nang may determinasyon ng isang incoming 1st Year IT Student mula sa Camotes Islands.*
