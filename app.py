import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Google Floats Game", page_icon="☁️", layout="wide")

st.markdown("""
    <style>
        /* Tối ưu không gian hiển thị trên mobile và desktop */
        .block-container { padding-top: 1.5rem; padding-bottom: 1rem; max-width: 1000px; }
        iframe { display: block; margin: 0 auto; border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }
    </style>
""", unsafe_allow_html=True)

st.title("☁️ Trò Chơi Đám Mây Bay (Google Floats)")
st.caption("📱 **Trên điện thoại:** Chạm vào màn hình để bay | 💻 **Trên máy tính:** Bấm **Spacebar** hoặc Click chuột")

game_html = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
    * {
        box-sizing: border-box;
        -webkit-touch-callout: none;
        -webkit-user-select: none;
        user-select: none;
    }
    body, html { 
        margin: 0; 
        padding: 0; 
        width: 100%; 
        height: 100%; 
        overflow: hidden; 
        background-color: #f0f9ff; 
        display: flex; 
        justify-content: center; 
        align-items: center; 
        font-family: system-ui, -apple-system, sans-serif;
        touch-action: manipulation;
    }
    #gameContainer { 
        position: relative; 
        width: 100%; 
        max-width: 480px; 
        height: 100vh; 
        max-height: 720px; 
        overflow: hidden; 
        border-radius: 16px; 
        box-shadow: 0 12px 32px rgba(2, 132, 199, 0.25);
        background: linear-gradient(to bottom, #0284c7 0%, #38bdf8 60%, #bae6fd 100%);
    }
    canvas { 
        width: 100%; 
        height: 100%; 
        display: block; 
    }
</style>
</head>
<body>
    <div id="gameContainer">
        <canvas id="gameCanvas"></canvas>
    </div>

<script>
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const container = document.getElementById('gameContainer');

// Tự động điều chỉnh kích thước Canvas theo kích thước thực tế
let GAME_WIDTH = 400;
let GAME_HEIGHT = 600;

function resizeCanvas() {
    GAME_WIDTH = container.clientWidth;
    GAME_HEIGHT = container.clientHeight;
    canvas.width = GAME_WIDTH;
    canvas.height = GAME_HEIGHT;
}
resizeCanvas();
window.addEventListener('resize', resizeCanvas);

let cloud = { x: 60, y: 250, width: 55, height: 40, gravity: 0.35, lift: -7, velocity: 0, rotation: 0 };
let obstacles = [];
let windParticles = [];
let frameCount = 0;
let score = 0;
let gameOver = false;
let gameStarted = false;

let shakeTime = 0;
let droppedUmbrella = { x: 0, y: 0, vx: 0, vy: 0, rot: 0 };

let bgCloudX = 0;
let bgHillX = 0;

// --- HỆ THỐNG ÂM THANH (WEB AUDIO API) ---
const AudioCtx = window.AudioContext || window.webkitAudioContext;
let audioCtx = null;

function initAudio() {
    if (!audioCtx) {
        audioCtx = new AudioCtx();
    }
}

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

function playScoreSound() {
    if (!audioCtx) return;
    let osc = audioCtx.createOscillator();
    let gain = audioCtx.createGain();
    osc.type = 'triangle';
    osc.frequency.setValueAtTime(523.25, audioCtx.currentTime);
    osc.frequency.setValueAtTime(659.25, audioCtx.currentTime + 0.08);
    gain.gain.setValueAtTime(0.15, audioCtx.currentTime);
    gain.gain.linearRampToValueAtTime(0.01, audioCtx.currentTime + 0.2);
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    osc.start();
    osc.stop(audioCtx.currentTime + 0.2);
}

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

function triggerGameOver() {
    gameOver = true;
    shakeTime = 15;
    playHitSound();

    droppedUmbrella = {
        x: cloud.x + 28,
        y: cloud.y - 8,
        vx: 3 + Math.random() * 2,
        vy: -5,
        rot: 0
    };
}

function handleInput(e) {
    if (e) e.preventDefault();
    initAudio();
    if (gameOver) { resetGame(); return; }
    if (!gameStarted) { gameStarted = true; loop(); }
    
    cloud.velocity = cloud.lift;
    playJumpSound();

    for (let i = 0; i < 4; i++) {
        windParticles.push({
            x: cloud.x + 15 + Math.random() * 30,
            y: cloud.y + 35,
            vx: -1 - Math.random() * 2,
            vy: 2 + Math.random() * 2,
            life: 1.0,
            size: 3 + Math.random() * 4
        });
    }
}

// Bắt cả sự kiện bàn phím, click chuột và chạm cảm ứng mobile
window.addEventListener('keydown', (e) => { if (e.code === 'Space') handleInput(e); });
canvas.addEventListener('click', handleInput);
canvas.addEventListener('touchstart', handleInput, { passive: false });

// --- VẼ MÔI TRƯỜNG & CHUYỂN ĐỘNG NỀN ---
function drawBackground() {
    if (gameStarted && !gameOver) {
        bgCloudX = (bgCloudX - 0.8) % GAME_WIDTH;
        bgHillX = (bgHillX - 2.0) % GAME_WIDTH;
    }

    ctx.fillStyle = 'rgba(255, 255, 255, 0.35)';
    for (let offset of [bgCloudX, bgCloudX + GAME_WIDTH]) {
        ctx.beginPath();
        ctx.arc(offset + GAME_WIDTH * 0.2, 50, 30, 0, Math.PI * 2);
        ctx.arc(offset + GAME_WIDTH * 0.3, 45, 40, 0, Math.PI * 2);
        ctx.arc(offset + GAME_WIDTH * 0.4, 50, 30, 0, Math.PI * 2);
        ctx.fill();

        ctx.beginPath();
        ctx.arc(offset + GAME_WIDTH * 0.7, 80, 25, 0, Math.PI * 2);
        ctx.arc(offset + GAME_WIDTH * 0.8, 75, 35, 0, Math.PI * 2);
        ctx.arc(offset + GAME_WIDTH * 0.9, 80, 25, 0, Math.PI * 2);
        ctx.fill();
    }

    for (let offset of [bgHillX, bgHillX + GAME_WIDTH]) {
        ctx.fillStyle = '#65a30d';
        ctx.beginPath();
        ctx.arc(offset + GAME_WIDTH * 0.3, GAME_HEIGHT + 120, GAME_WIDTH * 0.6, 0, Math.PI * 2);
        ctx.fill();

        ctx.fillStyle = '#4d7c0f';
        ctx.beginPath();
        ctx.arc(offset + GAME_WIDTH * 0.8, GAME_HEIGHT + 100, GAME_WIDTH * 0.55, 0, Math.PI * 2);
        ctx.fill();
    }
}

function drawDroppedUmbrella() {
    if (!gameOver) return;

    ctx.save();
    ctx.translate(droppedUmbrella.x, droppedUmbrella.y);
    ctx.rotate(droppedUmbrella.rot);

    ctx.fillStyle = '#f59e0b';
    ctx.beginPath();
    ctx.arc(0, 0, 20, Math.PI, 0);
    ctx.fill();

    ctx.strokeStyle = '#b45309';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.lineTo(0, 18);
    ctx.stroke();

    ctx.restore();

    droppedUmbrella.x += droppedUmbrella.vx;
    droppedUmbrella.y += droppedUmbrella.vy;
    droppedUmbrella.vy += 0.3;
    droppedUmbrella.rot += 0.15;
}

function drawWindParticles() {
    for (let i = windParticles.length - 1; i >= 0; i--) {
        let p = windParticles[i];
        ctx.fillStyle = `rgba(255, 255, 255, ${p.life})`;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
        ctx.fill();

        p.x += p.vx;
        p.y += p.vy;
        p.life -= 0.05;

        if (p.life <= 0) {
            windParticles.splice(i, 1);
        }
    }
}

function drawPlayer(x, y) {
    ctx.save();
    ctx.translate(x + 28, y + 20);
    ctx.rotate(cloud.rotation);
    ctx.translate(-(x + 28), -(y + 20));

    if (!gameOver) {
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
    }

    ctx.fillStyle = 'white';
    ctx.beginPath();
    ctx.arc(x + 15, y + 20, 14, 0, Math.PI * 2);
    ctx.arc(x + 28, y + 12, 18, 0, Math.PI * 2);
    ctx.arc(x + 42, y + 20, 14, 0, Math.PI * 2);
    ctx.fill();

    if (gameOver) {
        ctx.strokeStyle = '#0f172a';
        ctx.lineWidth = 2;

        ctx.beginPath();
        ctx.moveTo(x + 20, y + 13); ctx.lineTo(x + 26, y + 19);
        ctx.moveTo(x + 26, y + 13); ctx.lineTo(x + 20, y + 19);
        ctx.stroke();

        ctx.beginPath();
        ctx.moveTo(x + 30, y + 13); ctx.lineTo(x + 36, y + 19);
        ctx.moveTo(x + 36, y + 13); ctx.lineTo(x + 30, y + 19);
        ctx.stroke();

        ctx.beginPath();
        ctx.arc(x + 28, y + 24, 4, Math.PI, 0);
        ctx.stroke();
    } else {
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

    ctx.restore();
}

function drawCrow(x, y, frame) {
    let wingOffset = Math.sin(frame * 0.18) * 12;

    ctx.fillStyle = '#0f172a';
    ctx.beginPath();
    ctx.ellipse(x + 30, y + 25, 22, 15, 0, 0, Math.PI * 2);
    ctx.fill();

    ctx.beginPath();
    ctx.arc(x + 12, y + 18, 12, 0, Math.PI * 2);
    ctx.fill();

    ctx.fillStyle = '#f97316';
    ctx.beginPath();
    ctx.moveTo(x + 4, y + 15);
    ctx.lineTo(x - 12, y + 20);
    ctx.lineTo(x + 4, y + 24);
    ctx.closePath();
    ctx.fill();

    ctx.fillStyle = '#ef4444';
    ctx.beginPath();
    ctx.arc(x + 10, y + 15, 3.5, 0, Math.PI * 2);
    ctx.fill();

    ctx.fillStyle = '#1e293b';
    ctx.beginPath();
    ctx.moveTo(x + 25, y + 20);
    ctx.quadraticCurveTo(x + 35, y - 5 + wingOffset, x + 50, y + 5 + wingOffset);
    ctx.quadraticCurveTo(x + 35, y + 25, x + 25, y + 20);
    ctx.fill();

    ctx.fillStyle = '#0f172a';
    ctx.beginPath();
    ctx.moveTo(x + 48, y + 20);
    ctx.lineTo(x + 65, y + 15);
    ctx.lineTo(x + 62, y + 28);
    ctx.closePath();
    ctx.fill();
}

function drawThunderCloud(x, y) {
    ctx.fillStyle = '#334155';
    ctx.beginPath();
    ctx.arc(x + 20, y + 25, 18, 0, Math.PI * 2);
    ctx.arc(x + 35, y + 12, 22, 0, Math.PI * 2);
    ctx.arc(x + 52, y + 25, 18, 0, Math.PI * 2);
    ctx.fill();

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

    cloud.rotation = Math.min(Math.PI / 6, Math.max(-Math.PI / 6, cloud.velocity * 0.05));

    if (cloud.y + cloud.height > GAME_HEIGHT - 30 || cloud.y < -10) {
        triggerGameOver();
    }

    frameCount++;

    if (frameCount % 10 === 0) {
        score += 1;
    }

    if (frameCount % 75 === 0) {
        let type = Math.random() > 0.5 ? 'crow' : 'cloud';
        let obsY = Math.floor(Math.random() * (GAME_HEIGHT - 220)) + 40;
        obstacles.push({
            x: GAME_WIDTH,
            y: obsY,
            width: 65,
            height: 50,
            type: type
        });
    }

    for (let i = 0; i < obstacles.length; i++) {
        obstacles[i].x -= 4.0;

        if (cloud.x + 10 < obstacles[i].x + obstacles[i].width &&
            cloud.x + cloud.width - 10 > obstacles[i].x &&
            cloud.y + 5 < obstacles[i].y + obstacles[i].height &&
            cloud.y + cloud.height - 5 > obstacles[i].y) {
            triggerGameOver();
        }
    }

    if (obstacles.length > 0 && obstacles[0].x < -70) {
        obstacles.shift();
        score += 10;
        playScoreSound();
    }
}

function draw() {
    ctx.save();

    if (shakeTime > 0) {
        let dx = (Math.random() - 0.5) * 12;
        let dy = (Math.random() - 0.5) * 12;
        ctx.translate(dx, dy);
        shakeTime--;
    }

    ctx.clearRect(-20, -20, GAME_WIDTH + 40, GAME_HEIGHT + 40);

    drawBackground();
    drawWindParticles();
    drawPlayer(cloud.x, cloud.y);
    drawDroppedUmbrella();

    obstacles.forEach(obs => {
        if (obs.type === 'crow') {
            drawCrow(obs.x, obs.y, frameCount);
        } else {
            drawThunderCloud(obs.x, obs.y);
        }
    });

    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 28px monospace';
    ctx.textAlign = 'right';
    ctx.shadowColor = 'rgba(0,0,0,0.3)';
    ctx.shadowBlur = 4;
    ctx.fillText(String(score).padStart(6, '0'), GAME_WIDTH - 20, 45);
    ctx.shadowBlur = 0;

    if (!gameStarted) {
        ctx.fillStyle = 'rgba(0,0,0,0.45)';
        ctx.fillRect(0, 0, GAME_WIDTH, GAME_HEIGHT);
        ctx.fillStyle = 'white';
        ctx.font = 'bold 20px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('Chạm hoặc Space để BẮT ĐẦU', GAME_WIDTH / 2, GAME_HEIGHT / 2);
    }

    if (gameOver) {
        ctx.fillStyle = 'rgba(225, 29, 72, 0.85)';
        ctx.fillRect(0, 0, GAME_WIDTH, GAME_HEIGHT);
        ctx.fillStyle = 'white';
        ctx.font = 'bold 28px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('GAME OVER!', GAME_WIDTH / 2, GAME_HEIGHT / 2 - 20);
        ctx.font = '18px sans-serif';
        ctx.fillText('Điểm số: ' + score, GAME_WIDTH / 2, GAME_HEIGHT / 2 + 20);
        ctx.fillText('Chạm để CHƠI LẠI', GAME_WIDTH / 2, GAME_HEIGHT / 2 + 60);
    }

    ctx.restore();
}

function resetGame() {
    cloud.y = GAME_HEIGHT / 2 - 50;
    cloud.velocity = 0;
    cloud.rotation = 0;
    obstacles = [];
    windParticles = [];
    score = 0;
    frameCount = 0;
    gameOver = false;
    gameStarted = true;
    shakeTime = 0;
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

components.html(game_html, height=730)
