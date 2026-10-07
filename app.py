import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Google Floats Game", page_icon="☁️", layout="wide")

st.markdown("""
    <style>
        .block-container { padding-top: 1rem; padding-bottom: 1rem; max-width: 1200px; }
        iframe { display: block; margin: 0 auto; border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.25); }
    </style>
""", unsafe_allow_html=True)

st.title("☁️ Trò Chơi Đám Mây Bay (Google Floats)")
st.caption("💻 **Màn hình ngang Laptop** | 🌄 **Đồi nhấp nhô cao thấp đậm nhạt** | ☁️ **Mây thiết kế mềm mại**")

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
        max-width: 960px; 
        height: 100vh; 
        max-height: 540px; 
        overflow: hidden; 
        border-radius: 16px; 
        box-shadow: 0 12px 32px rgba(2, 132, 199, 0.25);
        background: linear-gradient(to bottom, #0284c7 0%, #38bdf8 65%, #bae6fd 100%);
    }
    @media (max-width: 600px) {
        #gameContainer {
            max-width: 100%;
            max-height: 100vh;
        }
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

let GAME_WIDTH = 800;
let GAME_HEIGHT = 450;

function resizeCanvas() {
    GAME_WIDTH = container.clientWidth;
    GAME_HEIGHT = container.clientHeight;
    canvas.width = GAME_WIDTH;
    canvas.height = GAME_HEIGHT;
}
resizeCanvas();
window.addEventListener('resize', resizeCanvas);

let cloud = { x: 100, y: 180, width: 60, height: 42, gravity: 0.35, lift: -7, velocity: 0, rotation: 0 };
let obstacles = [];
let windParticles = [];
let frameCount = 0;
let score = 0;
let gameOver = false;
let gameStarted = false;
let isMuted = false;

let shakeTime = 0;
let droppedUmbrella = { x: 0, y: 0, vx: 0, vy: 0, rot: 0 };

let bgCloudX = 0;
let bgHillFarX = 0;
let bgHillNearX = 0;

// --- HỆ THỐNG ÂM THANH & NHẠC NỀN ---
const AudioCtx = window.AudioContext || window.webkitAudioContext;
let audioCtx = null;
let bgmTimer = null;
let bgmNoteIndex = 0;

const bgmMelody = [
    261.63, 329.63, 392.00, 523.25, 392.00, 329.63,
    293.66, 349.23, 440.00, 587.33, 440.00, 349.23,
    329.63, 392.00, 493.88, 659.25, 493.88, 392.00,
    349.23, 440.00, 523.25, 698.46, 523.25, 440.00
];

function initAudio() {
    if (!audioCtx) audioCtx = new AudioCtx();
    if (audioCtx.state === 'suspended') audioCtx.resume();
}

function startBGM() {
    if (bgmTimer || isMuted) return;
    bgmNoteIndex = 0;
    bgmTimer = setInterval(() => {
        if (!gameStarted || gameOver || isMuted || !audioCtx) return;
        let freq = bgmMelody[bgmNoteIndex];
        let osc = audioCtx.createOscillator();
        let gain = audioCtx.createGain();
        osc.type = 'square';
        osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
        gain.gain.setValueAtTime(0.025, audioCtx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.18);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start();
        osc.stop(audioCtx.currentTime + 0.18);
        bgmNoteIndex = (bgmNoteIndex + 1) % bgmMelody.length;
    }, 200);
}

function stopBGM() {
    if (bgmTimer) {
        clearInterval(bgmTimer);
        bgmTimer = null;
    }
}

function playJumpSound() {
    if (!audioCtx || isMuted) return;
    let osc = audioCtx.createOscillator();
    let gain = audioCtx.createGain();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(320, audioCtx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(640, audioCtx.currentTime + 0.1);
    gain.gain.setValueAtTime(0.12, audioCtx.currentTime);
    gain.gain.linearRampToValueAtTime(0.01, audioCtx.currentTime + 0.1);
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    osc.start();
    osc.stop(audioCtx.currentTime + 0.1);
}

function playScoreSound() {
    if (!audioCtx || isMuted) return;
    let osc = audioCtx.createOscillator();
    let gain = audioCtx.createGain();
    osc.type = 'triangle';
    osc.frequency.setValueAtTime(523.25, audioCtx.currentTime);
    osc.frequency.setValueAtTime(659.25, audioCtx.currentTime + 0.08);
    gain.gain.setValueAtTime(0.12, audioCtx.currentTime);
    gain.gain.linearRampToValueAtTime(0.01, audioCtx.currentTime + 0.2);
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    osc.start();
    osc.stop(audioCtx.currentTime + 0.2);
}

function playHitSound() {
    if (!audioCtx || isMuted) return;
    let osc = audioCtx.createOscillator();
    let gain = audioCtx.createGain();
    osc.type = 'sawtooth';
    osc.frequency.setValueAtTime(180, audioCtx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(40, audioCtx.currentTime + 0.3);
    gain.gain.setValueAtTime(0.2, audioCtx.currentTime);
    gain.gain.linearRampToValueAtTime(0.01, audioCtx.currentTime + 0.3);
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    osc.start();
    osc.stop(audioCtx.currentTime + 0.3);
}

function triggerGameOver() {
    gameOver = true;
    shakeTime = 15;
    stopBGM();
    playHitSound();

    droppedUmbrella = {
        x: cloud.x + 30,
        y: cloud.y - 10,
        vx: 3 + Math.random() * 2,
        vy: -5,
        rot: 0
    };
}

function handleInput(e) {
    if (e && e.target && e.target.id === 'muteBtn') return;
    if (e) e.preventDefault();
    initAudio();
    
    if (gameOver) { resetGame(); return; }
    if (!gameStarted) { 
        gameStarted = true; 
        startBGM();
        loop(); 
    }
    
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

window.addEventListener('keydown', (e) => { if (e.code === 'Space') handleInput(e); });
canvas.addEventListener('click', handleInput);
canvas.addEventListener('touchstart', handleInput, { passive: false });

// --- VẼ ĐỒI NÚI (ĐỒI CAO/THẤP - ĐẬM/NHẠT) & MÂY NỀN MỚI ---
function drawBackground() {
    if (gameStarted && !gameOver) {
        bgCloudX = (bgCloudX - 0.5) % GAME_WIDTH;
        bgHillFarX = (bgHillFarX - 1.0) % GAME_WIDTH;
        bgHillNearX = (bgHillNearX - 2.2) % GAME_WIDTH;
    }

    // 1. Mây nền trôi (Thiết kế bồng bềnh hơn)
    ctx.fillStyle = 'rgba(255, 255, 255, 0.4)';
    for (let offset of [bgCloudX, bgCloudX + GAME_WIDTH]) {
        // Cụm mây xa 1
        ctx.beginPath();
        ctx.arc(offset + 100, 60, 22, 0, Math.PI * 2);
        ctx.arc(offset + 130, 50, 30, 0, Math.PI * 2);
        ctx.arc(offset + 165, 60, 24, 0, Math.PI * 2);
        ctx.fill();

        // Cụm mây xa 2
        ctx.beginPath();
        ctx.arc(offset + 500, 90, 20, 0, Math.PI * 2);
        ctx.arc(offset + 530, 80, 28, 0, Math.PI * 2);
        ctx.arc(offset + 560, 90, 22, 0, Math.PI * 2);
        ctx.fill();
    }

    // 2. Dãy đồi xa (ĐỒI CAO - NHẠT MÀU - XANH SƯƠNG)
    ctx.fillStyle = '#86efac'; // Màu xanh nhạt tươi sáng
    for (let offset of [bgHillFarX, bgHillFarX + GAME_WIDTH]) {
        ctx.beginPath();
        // Đồi cao 1
        ctx.arc(offset + GAME_WIDTH * 0.2, GAME_HEIGHT + 180, GAME_WIDTH * 0.38, 0, Math.PI * 2);
        // Đồi cao 2
        ctx.arc(offset + GAME_WIDTH * 0.7, GAME_HEIGHT + 210, GAME_WIDTH * 0.42, 0, Math.PI * 2);
        ctx.fill();
    }

    // 3. Dãy đồi gần (ĐỒI THẤP HƠN - ĐẬM MÀU - XANH LÁ CÂY ĐẬM)
    ctx.fillStyle = '#15803d'; // Màu xanh lá cây đậm nét
    for (let offset of [bgHillNearX, bgHillNearX + GAME_WIDTH]) {
        ctx.beginPath();
        // Đồi thấp 1
        ctx.arc(offset + GAME_WIDTH * 0.05, GAME_HEIGHT + 230, GAME_WIDTH * 0.32, 0, Math.PI * 2);
        // Đồi thấp 2
        ctx.arc(offset + GAME_WIDTH * 0.45, GAME_HEIGHT + 250, GAME_WIDTH * 0.35, 0, Math.PI * 2);
        // Đồi thấp 3
        ctx.arc(offset + GAME_WIDTH * 0.85, GAME_HEIGHT + 240, GAME_WIDTH * 0.3, 0, Math.PI * 2);
        ctx.fill();
    }
}

// --- VẼ ĐÁM MÂY NHÂN VẬT (SỬA LẠI ĐẸP & MỀM MẠI HƠN) ---
function drawPlayer(x, y) {
    ctx.save();
    ctx.translate(x + 30, y + 21);
    ctx.rotate(cloud.rotation);
    ctx.translate(-(x + 30), -(y + 21));

    // Cái Ô vàng nhỏ nhắn phía trên đám mây
    if (!gameOver) {
        ctx.fillStyle = '#f59e0b';
        ctx.beginPath();
        ctx.arc(x + 30, y - 8, 18, Math.PI, 0);
        ctx.fill();
        ctx.strokeStyle = '#b45309';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(x + 30, y - 8);
        ctx.lineTo(x + 30, y + 8);
        ctx.stroke();
    }

    // Thân Đám mây (Vẽ các đường cong bóng mịn)
    ctx.fillStyle = '#ffffff';
    ctx.beginPath();
    ctx.arc(x + 16, y + 24, 14, 0, Math.PI * 2);
    ctx.arc(x + 30, y + 15, 18, 0, Math.PI * 2);
    ctx.arc(x + 45, y + 24, 14, 0, Math.PI * 2);
    ctx.arc(x + 23, y + 28, 12, 0, Math.PI * 2);
    ctx.arc(x + 38, y + 28, 12, 0, Math.PI * 2);
    ctx.fill();

    // Mắt và Miệng Nhân Vật
    if (gameOver) {
        ctx.strokeStyle = '#0f172a';
        ctx.lineWidth = 2;

        ctx.beginPath();
        ctx.moveTo(x + 22, y + 16); ctx.lineTo(x + 28, y + 22);
        ctx.moveTo(x + 28, y + 16); ctx.lineTo(x + 22, y + 22);
        ctx.stroke();

        ctx.beginPath();
        ctx.moveTo(x + 32, y + 16); ctx.lineTo(x + 38, y + 22);
        ctx.moveTo(x + 38, y + 16); ctx.lineTo(x + 32, y + 22);
        ctx.stroke();

        ctx.beginPath();
        ctx.arc(x + 30, y + 27, 4, Math.PI, 0);
        ctx.stroke();
    } else {
        // Mắt đen xoe tròn
        ctx.fillStyle = '#0f172a';
        ctx.beginPath();
        ctx.arc(x + 24, y + 19, 2.5, 0, Math.PI * 2);
        ctx.arc(x + 36, y + 19, 2.5, 0, Math.PI * 2);
        ctx.fill();

        // 2 Má hồng dễ thương
        ctx.fillStyle = 'rgba(f4, 63, 94, 0.35)';
        ctx.beginPath();
        ctx.arc(x + 20, y + 23, 3.5, 0, Math.PI * 2);
        ctx.arc(x + 40, y + 23, 3.5, 0, Math.PI * 2);
        ctx.fill();

        // Nụ cười
        ctx.strokeStyle = '#0f172a';
        ctx.lineWidth = 1.8;
        ctx.beginPath();
        ctx.arc(x + 30, y + 21, 4, 0, Math.PI, false);
        ctx.stroke();
    }

    ctx.restore();
}

function drawDroppedUmbrella() {
    if (!gameOver) return;

    ctx.save();
    ctx.translate(droppedUmbrella.x, droppedUmbrella.y);
    ctx.rotate(droppedUmbrella.rot);

    ctx.fillStyle = '#f59e0b';
    ctx.beginPath();
    ctx.arc(0, 0, 18, Math.PI, 0);
    ctx.fill();

    ctx.strokeStyle = '#b45309';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.lineTo(0, 16);
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

        if (p.life <= 0) windParticles.splice(i, 1);
    }
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

    // Ranh giới chạm đất / va chạm
    if (cloud.y + cloud.height > GAME_HEIGHT - 25 || cloud.y < -10) {
        triggerGameOver();
    }

    frameCount++;
    if (frameCount % 10 === 0) score += 1;

    if (frameCount % 70 === 0) {
        let type = Math.random() > 0.5 ? 'crow' : 'cloud';
        let obsY = Math.floor(Math.random() * (GAME_HEIGHT - 200)) + 30;
        obstacles.push({
            x: GAME_WIDTH,
            y: obsY,
            width: 60,
            height: 48,
            type: type
        });
    }

    for (let i = 0; i < obstacles.length; i++) {
        obstacles[i].x -= 4.5;

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

function drawUI() {
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 28px monospace';
    ctx.textAlign = 'right';
    ctx.shadowColor = 'rgba(0,0,0,0.3)';
    ctx.shadowBlur = 4;
    ctx.fillText(String(score).padStart(6, '0'), GAME_WIDTH - 20, 45);
    ctx.shadowBlur = 0;

    ctx.font = '22px sans-serif';
    ctx.fillText(isMuted ? '🔇' : '🔊', GAME_WIDTH - 160, 42);

    if (!gameStarted) {
        ctx.fillStyle = 'rgba(0,0,0,0.4)';
        ctx.fillRect(0, 0, GAME_WIDTH, GAME_HEIGHT);
        ctx.fillStyle = 'white';
        ctx.font = 'bold 22px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('Nhấn Space hoặc Chạm màn hình để BẮT ĐẦU', GAME_WIDTH / 2, GAME_HEIGHT / 2);
    }

    if (gameOver) {
        ctx.fillStyle = 'rgba(225, 29, 72, 0.85)';
        ctx.fillRect(0, 0, GAME_WIDTH, GAME_HEIGHT);
        ctx.fillStyle = 'white';
        ctx.font = 'bold 30px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('GAME OVER!', GAME_WIDTH / 2, GAME_HEIGHT / 2 - 20);
        ctx.font = '20px sans-serif';
        ctx.fillText('Điểm số: ' + score, GAME_WIDTH / 2, GAME_HEIGHT / 2 + 20);
        ctx.fillText('Chạm/Bấm Space để CHƠI LẠI', GAME_WIDTH / 2, GAME_HEIGHT / 2 + 60);
    }
}

function toggleMute(e) {
    if (e) e.stopPropagation();
    isMuted = !isMuted;
    if (isMuted) {
        stopBGM();
    } else if (gameStarted && !gameOver) {
        startBGM();
    }
}

canvas.addEventListener('click', (e) => {
    let rect = canvas.getBoundingClientRect();
    let clickX = e.clientX - rect.left;
    let clickY = e.clientY - rect.top;
    if (clickX > GAME_WIDTH - 190 && clickX < GAME_WIDTH - 130 && clickY < 60) {
        toggleMute(e);
    }
});

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
        if (obs.type === 'crow') drawCrow(obs.x, obs.y, frameCount);
        else drawThunderCloud(obs.x, obs.y);
    });

    drawUI();
    ctx.restore();
}

function resetGame() {
    cloud.y = GAME_HEIGHT / 2 - 20;
    cloud.velocity = 0;
    cloud.rotation = 0;
    obstacles = [];
    windParticles = [];
    score = 0;
    frameCount = 0;
    gameOver = false;
    gameStarted = true;
    shakeTime = 0;
    startBGM();
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

components.html(game_html, height=560)
