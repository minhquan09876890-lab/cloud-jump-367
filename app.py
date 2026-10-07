import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Google Floats Game", page_icon="☁️", layout="centered")

st.title("☁️ Trò Chơi Đám Mây Bay (Google Floats)")
st.write("Sử dụng **Phím Cách (Spacebar)** hoặc **Click chuột** để giữ đám mây bay lên!")

# Mã HTML/JS xử lý game Đám mây bay mượt mà
game_html = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
    body { margin: 0; display: flex; justify-content: center; align-items: center; background-color: #f0f9ff; font-family: sans-serif; }
    #gameContainer { position: relative; width: 400px; height: 500px; overflow: hidden; border: 3px solid #0284c7; border-radius: 16px; }
    canvas { background: linear-gradient(to bottom, #38bdf8, #bae6fd); }
</style>
</head>
<body>
    <div id="gameContainer">
        <canvas id="gameCanvas" width="400" height="500"></canvas>
    </div>

<script>
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

let cloud = { x: 80, y: 250, width: 50, height: 35, gravity: 0.35, lift: -7, velocity: 0 };
let obstacles = [];
let frameCount = 0;
let score = 0;
let gameOver = false;
let gameStarted = false;

function handleInput() {
    if (gameOver) { resetGame(); return; }
    if (!gameStarted) { gameStarted = true; loop(); }
    cloud.velocity = cloud.lift;
}

window.addEventListener('keydown', (e) => { if (e.code === 'Space') { e.preventDefault(); handleInput(); } });
canvas.addEventListener('click', handleInput);

function drawCloud(x, y) {
    ctx.fillStyle = 'white';
    ctx.beginPath();
    ctx.arc(x + 15, y + 20, 12, 0, Math.PI * 2);
    ctx.arc(x + 25, y + 12, 16, 0, Math.PI * 2);
    ctx.arc(x + 35, y + 20, 12, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = '#0f172a';
    ctx.beginPath();
    ctx.arc(x + 21, y + 16, 2, 0, Math.PI * 2);
    ctx.arc(x + 29, y + 16, 2, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = '#0f172a';
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.arc(x + 25, y + 20, 4, 0, Math.PI, false);
    ctx.stroke();
}

function update() {
    if (gameOver || !gameStarted) return;

    cloud.velocity += cloud.gravity;
    cloud.y += cloud.velocity;

    if (cloud.y + cloud.height > canvas.height || cloud.y < 0) {
        gameOver = true;
    }

    frameCount++;
    if (frameCount % 90 === 0) {
        let obsHeight = Math.floor(Math.random() * 120) + 40;
        let obsY = Math.floor(Math.random() * (canvas.height - obsHeight));
        obstacles.push({ x: canvas.width, y: obsY, width: 25, height: obsHeight });
    }

    for (let i = 0; i < obstacles.length; i++) {
        obstacles[i].x -= 3.5;
        if (cloud.x < obstacles[i].x + obstacles[i].width &&
            cloud.x + cloud.width > obstacles[i].x &&
            cloud.y < obstacles[i].y + obstacles[i].height &&
            cloud.y + cloud.height > obstacles[i].y) {
            gameOver = true;
        }
    }

    if (obstacles.length > 0 && obstacles[0].x < -30) {
        obstacles.shift();
        score++;
    }
}

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    drawCloud(cloud.x, cloud.y);
    
    ctx.fillStyle = '#ef4444';
    obstacles.forEach(obs => ctx.fillRect(obs.x, obs.y, obs.width, obs.height));

    ctx.fillStyle = '#0f172a';
    ctx.font = 'bold 20px sans-serif';
    ctx.textAlign = 'right';
    ctx.fillText('Điểm: ' + score, canvas.width - 20, 35);

    if (!gameStarted) {
        ctx.fillStyle = 'rgba(0,0,0,0.4)';
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
        ctx.font = 'bold 28px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('GAME OVER!', canvas.width / 2, canvas.height / 2 - 15);
        ctx.font = '18px sans-serif';
        ctx.fillText('Điểm: ' + score, canvas.width / 2, canvas.height / 2 + 20);
        ctx.fillText('Click để chơi lại', canvas.width / 2, canvas.height / 2 + 55);
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

components.html(game_html, width=420, height=520)
