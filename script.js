const BACKEND = "https://youtube-downloader-4032.onrender.com"

let selectedFormat = "mp3"

const btnMp3 = document.getElementById("btn-mp3");
const btnMp4 = document.getElementById("btn-mp4");
const convertBtn = document.getElementById("convert-btn");
const urlInput = document.getElementById("yt-url");
const statusBox = document.getElementById("status-box");
const resultBox = document.getElementById("result-box");
const thumb = document.getElementById("thumb");
const videoTitle = document.getElementById("video-title");
const downloadLink = document.getElementById("download-link");

btnMp3.addEventListener("click", () => {
    selectedFormat = "mp3";
    btnMp3.classList.add("active");
    btnMp4.classList.remove("active");
    statusBox.classList.add("d-none");
    resultBox.classList.add("d-none");
});

btnMp4.addEventListener("click", () => {
    selectedFormat = "mp4";
    btnMp4.classList.add("active");
    btnMp4.classList.remove("active");
    statusBox.classList.add("d-none");
    resultBox.classList.add("d-none");
    showStatus("⚠️ MP4 download is currently under development. Please use MP3 for now.");
});

convertBtn.addEventListener("click", async () => {
    if (selectedFormat === "mp4") {
        showStatus("⚠️ MP4 download is currently under development. Please use MP3 for now.");
        return;
    }
    
    const url = urlInput.value.trim();
    
    if (!url) {
        showStatus("Please paste a YouTube URL first.");
        return;
    }
    
    showStatus("Converting... please wait.")
    resultBox.classList.add("d-none");
    
    try {
        const response = await
fetch(`${BACKEND}/api/convert`, {
    method: "POST", 
    headers: { "Content-Type": "application/json" }, 
    body: JSON.stringify({ url, format: selectedFormat })
    });
    
    const data = await response.json();
    
    if (!response.ok || !data.success) {
        showStatus(data.message || "Conversion failed. Try again.");
        return;
    }

statusBox.classList.add("d-none");
    thumb.src = data.thumbnail || "", 
    videoTitle.textContent = data.title || "YouTube Video";
    downloadLink.href = data.download_url;

downloadLink.setAttribute("download", data.title || "download");

resultBox.classList.remove("d-none");

    } catch (error) {
        showStatus("Something went wrong. Please try again.");
    }
});

function showStatus(msg) {
    statusBox.textContent = msg;

statusBox.classList.remove("d-none");
}
