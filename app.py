import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Google Floats Game", page_icon="☁️", layout="centered")

st.title("☁️ Trò Chơi Đám Mây Bay (Google Floats)")
st.write("Sử dụng **Phím Cách (Spacebar)** hoặc **Click chuột** để giữ đám mây bay lên!")

game_html = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
    body { margin: 0; display: flex; justify-content: center; align-items: center; background-color: #f0f9ff; font-family: sans-serif; }
    #gameContainer { position: relative; width: 400px; height: 600px; overflow: hidden; border: 3px solid #0284c7; border-radius: 16px; box-shadow: 0 10px 25px rgba(0,0,0,0.15); }
    canvas { background: linear-gradient(to bottom, #0284c7 0%, #38bdf8 60%, #bae6fd 100%); }
</style>
</head>
<body>
    <div id="gameContainer">
        <canvas id="gameCanvas" width="400" height="600"></canvas>
    </div>

<script>
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

let cloud = { x: 70, y: 250, width: 55, height: 40, gravity: 0.35, lift: -7, velocity: 0 };
let obstacles = [];
let frameCount = 0;
let score = 0;
let gameOver = false;
let gameStarted = false;

// --- HỆ THỐNG ÂM THANH (WEB AUDIO API) ---
const AudioCtx = window.AudioContext || window.webkitAudioContext;
let audioCtx = null;

function initAudio() {
    if (!audioCtx) {
        audioCtx = new AudioCtx();
    }
}

// 1. Âm thanh khi bay (Jump/Flap)
function playJumpSound() {
    if (!audioCtx) return;
    let osc = audioCtx.createOscillator();
    let gain = audioCtx.createGain();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(300, audioCtx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(600, audioCtx.currentTime + 0.1);
    gain.gain.setValueAtTime(0.2, audioCtx.currentTime);
    gain.gain.linearRampToValueAtTime(0.01, audioCtx.currentTime + 0.1);
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    osc.start();
    osc.stop(audioCtx.currentTime + 0.1);
}

// 2. Âm thanh khi cộng điểm (Score)
function playScoreSound() {
    if (!audioCtx) return;
    let osc = audioCtx.createOscillator();
    let gain = audioCtx.createGain();
    osc.type = 'triangle';
    osc.frequency.setValueAtTime(523.25, audioCtx.currentTime); // Note C5
    osc.frequency.setValueAtTime(659.25, audioCtx.currentTime + 0.08); // Note E5
    gain.gain.setValueAtTime(0.15, audioCtx.currentTime);
    gain.gain.linearRampToValueAtTime(0.01, audioCtx.currentTime + 0.2);
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    osc.start();
    osc.stop(audioCtx.currentTime + 0.2);
}

// 3. Âm thanh Va chạm (Game Over)
function playHitSound() {
    if (!audioCtx) return;
    let osc = audioCtx.createOscillator();
    let gain = audioCtx.createGain();
    osc.type = 'sawtooth';
    osc.frequency.setValueAtTime(180, audioCtx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(40, audioCtx.currentTime + 0.3);
    gain.gain.setValueAtTime(0.3, audioCtx.currentTime);
    gain.gain.linearRampToValueAtTime(0.01, audioCtx.currentTime + 0.3);
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    osc.start();
    osc.stop(audioCtx.currentTime + 0.3);
}

function handleInput() {
    initAudio();
    if (gameOver) { resetGame(); return; }
    if (!gameStarted) { gameStarted = true; loop(); }
    cloud.velocity = cloud.lift;
    playJumpSound();
}

window.addEventListener('keydown', (e) => { if (e.code === 'Space') { e.preventDefault(); handleInput(); } });
canvas.addEventListener('click', handleInput);

// --- VẼ MÔI TRƯỜNG & PHÔNG NỀN (BACKGROUND) ---
function drawBackground() {
    // Đám mây trang trí phía xa trên bầu trời
    ctx.fillStyle = 'rgba(255, 255, 255, 0.35)';
    ctx.beginPath();
    ctx.arc(80, 50, 30, 0, Math.PI * 2);
    ctx.arc(120, 45, 40, 0, Math.PI * 2);
    ctx.arc(160, 50, 30, 0, Math.PI * 2);
    ctx.fill();

    ctx.beginPath();
    ctx.arc(280, 80, 25, 0, Math.PI * 2);
    ctx.arc(315, 75, 35, 0, Math.PI * 2);
    ctx.arc(350, 80, 25, 0, Math.PI * 2);
    ctx.fill();

    // Ngọn đồi xanh lá phía dưới (như ảnh Google Floats)
    ctx.fillStyle = '#65a30d'; // Màu xanh đồi
    ctx.beginPath();
    ctx.arc(120, 720, 250, 0, Math.PI * 2);
    ctx.fill();

    ctx.fillStyle = '#4d7c0f'; // Ngọn đồi phụ
    ctx.beginPath();
    ctx.arc(340, 700, 220, 0, Math.PI * 2);
    ctx.fill();
}

// --- VẼ NHÂN VẬT ĐÁM MÂY CẦM DÙ ---
function drawPlayer(x, y) {
    // Dù vàng
    ctx.fillStyle = '#f59e0b';
    ctx.beginPath();
    ctx.arc(x + 28, y - 8, 20, Math.PI, 0);
    ctx.fill();
    ctx.strokeStyle = '#b45309';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(x + 28, y - 8);
    ctx.lineTo(x + 28, y + 10);
    ctx.stroke();

    // Thân mây trắng
    ctx.fillStyle = 'white';
    ctx.beginPath();
    ctx.arc(x + 15, y + 20, 14, 0, Math.PI * 2);
    ctx.arc(x + 28, y + 12, 18, 0, Math.PI * 2);
    ctx.arc(x + 42, y + 20, 14, 0, Math.PI * 2);
    ctx.fill();

    // Mắt & Miệng
    ctx.fillStyle = '#0f172a';
    ctx.beginPath();
    ctx.arc(x + 23, y + 16, 2.5, 0, Math.PI * 2);
    ctx.arc(x + 33, y + 16, 2.5, 0, Math.PI * 2);
    ctx.fill();

    ctx.strokeStyle = '#0f172a';
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.arc(x + 28, y + 20, 4, 0, Math.PI, false);
    ctx.stroke();
}

// --- 1. CON QUẠ ĐEN (KÍCH THƯỚC TO & THIẾT KẾ MỚI) ---
function drawCrow(x, y, frame) {
    let wingOffset = Math.sin(frame * 0.15) * 12; // Cánh vỗ sinh động

    // Thân quạ
    ctx.fillStyle = '#0f172a';
    ctx.beginPath();
    ctx.ellipse(x + 30, y + 25, 22, 15, 0, 0, Math.PI * 2);
    ctx.fill();

    // Đầu quạ
    ctx.beginPath();
    ctx.arc(x + 12, y + 18, 12, 0, Math.PI * 2);
    ctx.fill();

    // Mỏ quạ nhọn
    ctx.fillStyle = '#f97316';
    ctx.beginPath();
    ctx.moveTo(x + 4, y + 15);
    ctx.lineTo(x - 12, y + 20);
    ctx.lineTo(x + 4, y + 24);
    ctx.closePath();
    ctx.fill();

    // Mắt quạ đỏ ngầu
    ctx.fillStyle = '#ef4444';
    ctx.beginPath();
    ctx.arc(x + 10, y + 15, 3.5, 0, Math.PI * 2);
    ctx.fill();

    // Cánh quạ đen to vỗ
    ctx.fillStyle = '#1e293b';
    ctx.beginPath();
    ctx.moveTo(x + 25, y + 20);
    ctx.quadraticCurveTo(x + 35, y - 5 + wingOffset, x + 50, y + 5 + wingOffset);
    ctx.quadraticCurveTo(x + 35, y + 25, x + 25, y + 20);
    ctx.fill();

    // Đuôi quạ
    ctx.fillStyle = '#0f172a';
    ctx.beginPath();
    ctx.moveTo(x + 48, y + 20);
    ctx.lineTo(x + 65, y + 15);
    ctx.lineTo(x + 62, y + 28);
    ctx.closePath();
    ctx.fill();
}

// --- 2. ĐÁM MÂY ĐIỆN (KÍCH THƯỚC TO) ---
function drawThunderCloud(x, y) {
    // Thân mây xám sẫm to
    ctx.fillStyle = '#334155';
    ctx.beginPath();
    ctx.arc(x + 20, y + 25, 18, 0, Math.PI * 2);
    ctx.arc(x + 35, y + 12, 22, 0, Math.PI * 2);
    ctx.arc(x + 52, y + 25, 18, 0, Math.PI * 2);
    ctx.fill();

    // Tia sét to sắc nét
    ctx.fillStyle = '#facc15';
    ctx.beginPath();
    ctx.moveTo(x + 36, y + 32);
    ctx.lineTo(x + 24, y + 48);
    ctx.lineTo(x + 32, y + 48);
    ctx.lineTo(x + 22, y + 65);
    ctx.lineTo(x + 42, y + 42);
    ctx.lineTo(x + 34, y + 42);
    ctx.closePath();
    ctx.fill();
}

function update() {
    if (gameOver || !gameStarted) return;

    cloud.velocity += cloud.gravity;
    cloud.y += cloud.velocity;

    // Rơi đụng đồi hoặc bay đụng trần
    if (cloud.y + cloud.height > canvas.height - 50 || cloud.y < -10) {
        gameOver = true;
        playHitSound();
    }

    frameCount++;
    // Sinh chướng ngại vật ngẫu nhiên
    if (frameCount % 80 === 0) {
        let type = Math.random() > 0.5 ? 'crow' : 'cloud';
        let obsY = Math.floor(Math.random() * (canvas.height - 220)) + 40;
        
        // Kích thước chướng ngại vật TO NGHỆ THUẬT (65x50)
        obstacles.push({
            x: canvas.width,
            y: obsY,
            width: 65,
            height: 50,
            type: type
        });
    }

    // Di chuyển & va chạm
    for (let i = 0; i < obstacles.length; i++) {
        obstacles[i].x -= 3.8;

        // Xử lý va chạm
        if (cloud.x + 10 < obstacles[i].x + obstacles[i].width &&
            cloud.x + cloud.width - 10 > obstacles[i].x &&
            cloud.y + 5 < obstacles[i].y + obstacles[i].height &&
            cloud.y + cloud.height - 5 > obstacles[i].y) {
            gameOver = true;
            playHitSound();
        }
    }

    // Vượt qua chướng ngại vật -> Cộng điểm + Phát tiếng
    if (obstacles.length > 0 && obstacles[0].x < -70) {
        obstacles.shift();
        score++;
        playScoreSound();
    }
}

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    drawBackground();
    drawPlayer(cloud.x, cloud.y);

    // Vẽ chướng ngại vật
    obstacles.forEach(obs => {
        if (obs.type === 'crow') {
            drawCrow(obs.x, obs.y, frameCount);
        } else {
            drawThunderCloud(obs.x, obs.y);
        }
    });

    // Hiển thị Điểm số đẹp dạng Google
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 26px monospace';
    ctx.textAlign = 'right';
    ctx.shadowColor = 'rgba(0,0,0,0.3)';
    ctx.shadowBlur = 4;
    ctx.fillText('SCORE ' + String(score).padStart(5, '0'), canvas.width - 20, 45);
    ctx.shadowBlur = 0; // Reset hiệu ứng shadow

    if (!gameStarted) {
        ctx.fillStyle = 'rgba(0,0,0,0.45)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = 'white';
        ctx.font = 'bold 22px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('Click hoặc Space để BẮT ĐẦU', canvas.width / 2, canvas.height / 2);
    }

    if (gameOver) {
        ctx.fillStyle = 'rgba(225, 29, 72, 0.85)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = 'white';
        ctx.font = 'bold 30px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('GAME OVER!', canvas.width / 2, canvas.height / 2 - 20);
        ctx.font = '20px sans-serif';
        ctx.fillText('Điểm số: ' + score, canvas.width / 2, canvas.height / 2 + 20);
        ctx.fillText('Click để CHƠI LẠI', canvas.width / 2, canvas.height / 2 + 60);
    }
}

function resetGame() {
    cloud.y = 250;
    cloud.velocity = 0;
    obstacles = [];
    score = 0;
    frameCount = 0;
    gameOver = false;
    gameStarted = true;
    loop();
}

function loop() {
    update();
    draw();
    if (!gameOver && gameStarted) requestAnimationFrame(loop);
}

draw();
</script>
</body>
</html>
"""

components.html(game_html, width=420, height=620)
