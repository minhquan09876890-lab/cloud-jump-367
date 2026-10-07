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

let cloud = { x: 70, y: 250, width: 55, height: 40, gravity: 0.35, lift: -7, velocity: 0, rotation: 0 };
let obstacles = [];
let windParticles = []; // Mảng chứa hiệu ứng gợn gió khi nhảy
let frameCount = 0;
let score = 0;
let gameOver = false;
let gameStarted = false;

// Biến hiệu ứng Thua cuộc & Rung màn hình
let shakeTime = 0;
let droppedUmbrella = { x: 0, y: 0, vx: 0, vy: 0, rot: 0 };

// Biến điều khiển chuyển động nền
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
    shakeTime = 15; // Rung màn hình 15 frames
    playHitSound();

    // Khởi tạo hiệu ứng Dù bị văng ra khi thua
    droppedUmbrella = {
        x: cloud.x + 28,
        y: cloud.y - 8,
        vx: 3 + Math.random() * 2,
        vy: -5,
        rot: 0
    };
}

function handleInput() {
    initAudio();
    if (gameOver) { resetGame(); return; }
    if (!gameStarted) { gameStarted = true; loop(); }
    
    cloud.velocity = cloud.lift;
    playJumpSound();

    // TẠO HIỆU ỨNG NHẢY: Thêm tia gió bên dưới đám mây
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

window.addEventListener('keydown', (e) => { if (e.code === 'Space') { e.preventDefault(); handleInput(); } });
canvas.addEventListener('click', handleInput);

// --- VẼ MÔI TRƯỜNG & CHUYỂN ĐỘNG NỀN ---
function drawBackground() {
    if (gameStarted && !gameOver) {
        bgCloudX = (bgCloudX - 0.8) % 400;
        bgHillX = (bgHillX - 2.0) % 400;
    }

    ctx.fillStyle = 'rgba(255, 255, 255, 0.35)';
    for (let offset of [bgCloudX, bgCloudX + 400]) {
        ctx.beginPath();
        ctx.arc(offset + 80, 50, 30, 0, Math.PI * 2);
        ctx.arc(offset + 120, 45, 40, 0, Math.PI * 2);
        ctx.arc(offset + 160, 50, 30, 0, Math.PI * 2);
        ctx.fill();

        ctx.beginPath();
        ctx.arc(offset + 280, 80, 25, 0, Math.PI * 2);
        ctx.arc(offset + 315, 75, 35, 0, Math.PI * 2);
        ctx.arc(offset + 350, 80, 25, 0, Math.PI * 2);
        ctx.fill();
    }

    for (let offset of [bgHillX, bgHillX + 400]) {
        ctx.fillStyle = '#65a30d';
        ctx.beginPath();
        ctx.arc(offset + 120, 720, 250, 0, Math.PI * 2);
        ctx.fill();

        ctx.fillStyle = '#4d7c0f';
        ctx.beginPath();
        ctx.arc(offset + 340, 700, 220, 0, Math.PI * 2);
        ctx.fill();
    }
}

// --- VẼ VẬT THỂ DÙ RỜI RẠC KHI THUA ---
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

    // Cập nhật vị trí rơi chiếc dù
    droppedUmbrella.x += droppedUmbrella.vx;
    droppedUmbrella.y += droppedUmbrella.vy;
    droppedUmbrella.vy += 0.3; // Trọng lực dù
    droppedUmbrella.rot += 0.15;
}

// --- VẼ HIỆU ỨNG TIA GIÓ KHI NHẢY ---
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

// --- VẼ NHÂN VẬT ĐÁM MÂY (CÓ XOAY & MẮT KHI THUA) ---
function drawPlayer(x, y) {
    ctx.save();
    // Xoay đám mây theo góc velocity
    ctx.translate(x + 28, y + 20);
    ctx.rotate(cloud.rotation);
    ctx.translate(-(x + 28), -(y + 20));

    // Nếu chưa thua thì vẽ Dù vàng gắn liền
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

    // Thân mây
    ctx.fillStyle = 'white';
    ctx.beginPath();
    ctx.arc(x + 15, y + 20, 14, 0, Math.PI * 2);
    ctx.arc(x + 28, y + 12, 18, 0, Math.PI * 2);
    ctx.arc(x + 42, y + 20, 14, 0, Math.PI * 2);
    ctx.fill();

    // VẼ MẮT VÀ MIỆNG
    if (gameOver) {
        // Mắt x-x khi thua
        ctx.strokeStyle = '#0f172a';
        ctx.lineWidth = 2;

        // Mắt trái x
        ctx.beginPath();
        ctx.moveTo(x + 20, y + 13); ctx.lineTo(x + 26, y + 19);
        ctx.moveTo(x + 26, y + 13); ctx.lineTo(x + 20, y + 19);
        ctx.stroke();

        // Mắt phải x
        ctx.beginPath();
        ctx.moveTo(x + 30, y + 13); ctx.lineTo(x + 36, y + 19);
        ctx.moveTo(x + 36, y + 13); ctx.lineTo(x + 30, y + 19);
        ctx.stroke();

        // Miệng méo khi thua
        ctx.beginPath();
        ctx.arc(x + 28, y + 24, 4, Math.PI, 0);
        ctx.stroke();
    } else {
        // Mắt tròn bình thường
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

// --- CON QUẠ ĐEN ---
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

// --- ĐÁM MÂY ĐIỆN ---
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

    // HIỆU ỨNG NGHIÊNG ĐÁM MÂY: Nghiêng lên khi bay, ngửa xuống khi rơi
    cloud.rotation = Math.min(Math.PI / 6, Math.max(-Math.PI / 6, cloud.velocity * 0.05));

    if (cloud.y + cloud.height > canvas.height - 50 || cloud.y < -10) {
        triggerGameOver();
    }

    frameCount++;

    if (frameCount % 10 === 0) {
        score += 1;
    }

    if (frameCount % 75 === 0) {
        let type = Math.random() > 0.5 ? 'crow' : 'cloud';
        let obsY = Math.floor(Math.random() * (canvas.height - 220)) + 40;
        obstacles.push({
            x: canvas.width,
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

    // HIỆU ỨNG RUNG MÀN HÌNH (SCREEN SHAKE) KHI THUA
    if (shakeTime > 0) {
        let dx = (Math.random() - 0.5) * 12;
        let dy = (Math.random() - 0.5) * 12;
        ctx.translate(dx, dy);
        shakeTime--;
    }

    ctx.clearRect(-20, -20, canvas.width + 40, canvas.height + 40);

    drawBackground();
    drawWindParticles(); // Vẽ các gợn gió khi nhảy
    drawPlayer(cloud.x, cloud.y);
    drawDroppedUmbrella(); // Vẽ dù rơi khi thua

    obstacles.forEach(obs => {
        if (obs.type === 'crow') {
            drawCrow(obs.x, obs.y, frameCount);
        } else {
            drawThunderCloud(obs.x, obs.y);
        }
    });

    // Điểm số
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 28px monospace';
    ctx.textAlign = 'right';
    ctx.shadowColor = 'rgba(0,0,0,0.3)';
    ctx.shadowBlur = 4;
    ctx.fillText(String(score).padStart(6, '0'), canvas.width - 20, 45);
    ctx.shadowBlur = 0;

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

    ctx.restore();
}

function resetGame() {
    cloud.y = 250;
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

components.html(game_html, width=420, height=620)
