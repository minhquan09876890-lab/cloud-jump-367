import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Cloud Jump", page_icon="☁️")
st.title("☁️ Trò Chơi Đám Mây Nhảy")
st.write("Bấm **Phím Cách (Spacebar)** hoặc **Click chuột vào khung game** để nhảy!")

game_code = """
<!DOCTYPE html>
<html>
<head>
<style>
    body { margin: 0; display: flex; justify-content: center; background-color: #f0f3f8; }
    canvas { border: 2px solid #3b82f6; border-radius: 12px; background: #e0f2fe; }
</style>
</head>
<body>
<canvas id="gameCanvas" width="600" height="250"></canvas>
<script>
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
let cloud = { x: 50, y: 180, width: 50, height: 30, gravity: 0.6, lift: -10, velocity: 0, isGrounded: true };
let obstacles = [];
let frameCount = 0;
let score = 0;
let gameOver = false;

function jump() {
    if (gameOver) { resetGame(); return; }
    if (cloud.isGrounded) { cloud.velocity = cloud.lift; cloud.isGrounded = false; }
}

window.addEventListener('keydown', (e) => { if (e.code === 'Space') { e.preventDefault(); jump(); } });
canvas.addEventListener('click', jump);

function resetGame() {
    cloud.y = 180; cloud.velocity = 0; cloud.isGrounded = true;
    obstacles = []; score = 0; frameCount = 0; gameOver = false; loop();
}

function drawCloud(x, y) {
    ctx.fillStyle = '#60a5fa';
    ctx.beginPath();
    ctx.arc(x + 15, y + 15, 12, 0, Math.PI * 2);
    ctx.arc(x + 25, y + 8, 15, 0, Math.PI * 2);
    ctx.arc(x + 35, y + 15, 12, 0, Math.PI * 2);
    ctx.fill();
}

function update() {
    if (gameOver) return;
    cloud.velocity += cloud.gravity;
    cloud.y += cloud.velocity;
    if (cloud.y >= 180) { cloud.y = 180; cloud.velocity = 0; cloud.isGrounded = true; }

    frameCount++;
    if (frameCount % 90 === 0) {
        let height = Math.floor(Math.random() * 20) + 30;
        obstacles.push({ x: canvas.width, y: canvas.height - height - 10, width: 20, height: height });
    }

    for (let i = 0; i < obstacles.length; i++) {
        obstacles[i].x -= 5;
        if (cloud.x < obstacles[i].x + obstacles[i].width && cloud.x + cloud.width > obstacles[i].x &&
            cloud.y < obstacles[i].y + obstacles[i].height && cloud.y + cloud.height > obstacles[i].y) {
            gameOver = true;
        }
    }
    if (obstacles.length > 0 && obstacles[0].x < -20) { obstacles.shift(); score += 10; }
}

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.strokeStyle = '#94a3b8';
    ctx.beginPath(); ctx.moveTo(0, 210); ctx.lineTo(canvas.width, 210); ctx.stroke();
    drawCloud(cloud.x, cloud.y);
    ctx.fillStyle = '#ef4444';
    obstacles.forEach(obs => ctx.fillRect(obs.x, obs.y, obs.width, obs.height));
    ctx.fillStyle = '#1e293b'; ctx.font = 'bold 16px Arial'; ctx.fillText('Điểm: ' + score, 20, 30);

    if (gameOver) {
        ctx.fillStyle = '#dc2626'; ctx.font = 'bold 24px Arial'; ctx.textAlign = 'center';
        ctx.fillText('GAME OVER!', canvas.width / 2, 110);
        ctx.font = '16px Arial'; ctx.fillText('Nhấn Space hoặc Click để chơi lại', canvas.width / 2, 140);
        ctx.textAlign = 'start';
    }
}

function loop() { update(); draw(); if (!gameOver) requestAnimationFrame(loop); }
loop();
</script>
</body>
</html>
"""

components.html(game_code, height=300)
