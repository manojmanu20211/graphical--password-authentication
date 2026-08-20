const canvas = document.getElementById('imageCanvas');
const ctx = canvas.getContext('2d');
const img = document.getElementById('userImage');
const pointCountSpan = document.getElementById('pointCount');
const resetBtn = document.getElementById('resetBtn');
const submitBtn = document.getElementById('submitBtn');

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
        alert('You have already selected 5 points. Click Reset to start over.');
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
        submitBtn.disabled = false;
    }
});

function drawPoint(x, y, number) {
    ctx.beginPath();
    ctx.arc(x, y, 10, 0, 2 * Math.PI);
    ctx.fillStyle = 'rgba(255, 0, 0, 0.7)';
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
    submitBtn.disabled = true;
    
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(img, 0, 0);
});

submitBtn.addEventListener('click', function() {
    if (points.length !== maxPoints) {
        alert('Please select exactly 5 points.');
        return;
    }
    
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
    
    fetch('/save_points', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ points: points })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Registration successful! You can now login.');
            window.location.href = '/login';
        } else {
            alert('Error: ' + data.message);
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-check"></i> Complete Registration';
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fas fa-check"></i> Complete Registration';
    });
});
