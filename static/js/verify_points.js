const canvas = document.getElementById('imageCanvas');
const ctx = canvas.getContext('2d');
const img = document.getElementById('userImage');
const pointCountSpan = document.getElementById('pointCount');
const attemptsLeftSpan = document.getElementById('attemptsLeft');
const resetBtn = document.getElementById('resetBtn');
const verifyBtn = document.getElementById('verifyBtn');

let points = [];
const maxPoints = 5;

img.onload = function() {
    const maxWidth = 800;
    const maxHeight = 600;
    
    let width = img.naturalWidth;
    let height = img.naturalHeight;
    
    if (width > maxWidth) {
        height = (maxWidth / width) * height;
        width = maxWidth;
    }
    
    if (height > maxHeight) {
        width = (maxHeight / height) * width;
        height = maxHeight;
    }
    
    canvas.width = width;
    canvas.height = height;
    
    ctx.drawImage(img, 0, 0, width, height);
};

canvas.addEventListener('click', function(event) {
    if (points.length >= maxPoints) {
        alert('You have already clicked 5 points. Click Reset to start over.');
        return;
    }
    
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    
    const x = Math.round((event.clientX - rect.left) * scaleX);
    const y = Math.round((event.clientY - rect.top) * scaleY);
    
    points.push({ x: x, y: y });
    
    drawPoint(x, y, points.length);
    
    pointCountSpan.textContent = points.length;
    
    if (points.length === maxPoints) {
        verifyBtn.disabled = false;
    }
});

function drawPoint(x, y, number) {
    ctx.beginPath();
    ctx.arc(x, y, 10, 0, 2 * Math.PI);
    ctx.fillStyle = 'rgba(0, 123, 255, 0.7)';
    ctx.fill();
    ctx.strokeStyle = 'white';
    ctx.lineWidth = 2;
    ctx.stroke();
    
    ctx.fillStyle = 'white';
    ctx.font = 'bold 12px Arial';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(number.toString(), x, y);
}

resetBtn.addEventListener('click', function() {
    points = [];
    pointCountSpan.textContent = '0';
    verifyBtn.disabled = true;
    
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(img, 0, 0);
});

verifyBtn.addEventListener('click', function() {
    if (points.length !== maxPoints) {
        alert('Please click exactly 5 points.');
        return;
    }
    
    verifyBtn.disabled = true;
    verifyBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Verifying...';
    
    fetch('/check_points', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ points: points })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Login successful! Welcome to your dashboard.');
            window.location.href = '/dashboard';
        } else {
            alert(data.message);
            
            if (data.locked) {
                window.location.href = '/login';
            } else {
                const currentAttempts = parseInt(attemptsLeftSpan.textContent);
                attemptsLeftSpan.textContent = currentAttempts - 1;
                
                points = [];
                pointCountSpan.textContent = '0';
                verifyBtn.disabled = true;
                verifyBtn.innerHTML = '<i class="fas fa-check"></i> Verify & Login';
                
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                ctx.drawImage(img, 0, 0);
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
        verifyBtn.disabled = false;
        verifyBtn.innerHTML = '<i class="fas fa-check"></i> Verify & Login';
    });
});
