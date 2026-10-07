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
    #gameContainer { position: relative; width: 400px; height: 550px; overflow: hidden; border: 3px solid #0284c7; border-radius: 16px; }
    canvas { background: linear-gradient(to bottom, #38bdf8, #bae6fd); }
</style>
</head>
<body>
    <div id="gameContainer">
        <canvas id="gameCanvas" width="400" height="550"></canvas>
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

// Vẽ Nhân vật Đám Mây Trắng (Cầm Dù)
function drawPlayer(x, y) {
    // Dù vàng
    ctx.fillStyle = '#f59e0b';
    ctx.beginPath();
    ctx.arc(x + 25, y - 5, 18, Math.PI, 0);
    ctx.fill();
    ctx.strokeStyle = '#d97706';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(x + 25, y - 5);
    ctx.lineTo(x + 25, y + 10);
    ctx.stroke();

    // Thân đám mây trắng
    ctx.fillStyle = 'white';
    ctx.beginPath();
    ctx.arc(x + 15, y + 20, 12, 0, Math.PI * 2);
    ctx.arc(x + 25, y + 12, 16, 0, Math.PI * 2);
    ctx.arc(x + 35, y + 20, 12, 0, Math.PI * 2);
    ctx.fill();

    // Mắt & Miệng
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

// 1. Vẽ Chướng ngại vật: Con chim đen
function drawBird(x, y) {
    ctx.fillStyle = '#1e293b'; // Thân chim đen
    ctx.beginPath();
    ctx.arc(x + 15, y + 12, 10, 0, Math.PI * 2);
    ctx.fill();

    // Cánh chim
    ctx.beginPath();
    ctx.moveTo(x + 15, y + 10);
    ctx.lineTo(x + 5, y - 2);
    ctx.lineTo(x + 20, y + 8);
    ctx.fill();

    // Mỏ chim vàng
    ctx.fillStyle = '#f59e0b';
    ctx.beginPath();
    ctx.moveTo(x, y + 12);
    ctx.lineTo(x - 8, y + 10);
    ctx.lineTo(x, y + 16);
    ctx.fill();

    // Mắt
    ctx.fillStyle = 'white';
    ctx.beginPath();
    ctx.arc(x + 6, y + 10, 2.5, 0, Math.PI * 2);
    ctx.fill();
}

// 2. Vẽ Chướng ngại vật: Đám mây điện
function drawThunderCloud(x, y) {
    // Đám mây xám đen
    ctx.fillStyle = '#475569';
    ctx.beginPath();
    ctx.arc(x + 15, y + 20, 12, 0, Math.PI * 2);
    ctx.arc(x + 25, y + 10, 16, 0, Math.PI * 2);
    ctx.arc(x + 38, y + 20, 14, 0, Math.PI * 2);
    ctx.fill();

    // Tia sét vàng dưới đám mây
    ctx.fillStyle = '#eab308';
    ctx.beginPath();
    ctx.moveTo(x + 26, y + 26);
    ctx.lineTo(x + 18, y + 38);
    ctx.lineTo(x + 24, y + 38);
    ctx.lineTo(x + 20, y + 48);
    ctx.lineTo(x + 30, y + 34);
    ctx.lineTo(x + 24, y + 34);
    ctx.closePath();
    ctx.fill();
}

function update() {
    if (gameOver || !gameStarted) return;

    cloud.velocity += cloud.gravity;
    cloud.y += cloud.velocity;

    // Rơi quá thấp hoặc bay quá cao
    if (cloud.y + cloud.height > canvas.height || cloud.y < -10) {
        gameOver = true;
    }

    frameCount++;
    // Tạo chướng ngại vật ngẫu nhiên
    if (frameCount % 85 === 0) {
        let type = Math.random() > 0.5 ? 'bird' : 'cloud';
        let obsY = Math.floor(Math.random() * (canvas.height - 120)) + 30;
        obstacles.push({
            x: canvas.width,
            y: obsY,
            width: 35,
            height: 35,
            type: type
        });
    }

    // Di chuyển vật cản & kiểm tra va chạm
    for (let i = 0; i < obstacles.length; i++) {
        obstacles[i].x -= 3.8;

        if (cloud.x < obstacles[i].x + obstacles[i].width &&
            cloud.x + cloud.width > obstacles[i].x &&
            cloud.y < obstacles[i].y + obstacles[i].height &&
            cloud.y + cloud.height > obstacles[i].y) {
            gameOver = true;
        }
    }

    if (obstacles.length > 0 && obstacles[0].x < -40) {
        obstacles.shift();
        score++;
    }
}

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    drawPlayer(cloud.x, cloud.y);

    // Vẽ từng vật cản theo loại
    obstacles.forEach(obs => {
        if (obs.type === 'bird') {
            drawBird(obs.x, obs.y);
        } else {
            drawThunderCloud(obs.x, obs.y);
        }
    });

    // Hiển thị điểm số
    ctx.fillStyle = '#0f172a';
    ctx.font = 'bold 22px monospace';
    ctx.textAlign = 'right';
    ctx.fillText('SCORE: ' + String(score).padStart(6, '0'), canvas.width - 20, 40);

    if (!gameStarted) {
        ctx.fillStyle = 'rgba(0,0,0,0.4)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = 'white';
        ctx.font = 'bold 20px sans-serif';
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

components.html(game_html, width=420, height=570)
