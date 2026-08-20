const decryptModal = new bootstrap.Modal(document.getElementById('decryptModal'));
const decryptBtns = document.querySelectorAll('.decrypt-btn');
const confirmDecryptBtn = document.getElementById('confirmDecrypt');
const decryptForm = document.getElementById('decryptForm');

decryptBtns.forEach(btn => {
    btn.addEventListener('click', function() {
        const fileId = this.getAttribute('data-file-id');
        const filename = this.getAttribute('data-filename');
        
        document.getElementById('fileId').value = fileId;
        document.getElementById('modalFilename').textContent = filename;
        document.getElementById('decryptCodeword').value = '';
        
        decryptModal.show();
    });
});

confirmDecryptBtn.addEventListener('click', function() {
    const fileId = document.getElementById('fileId').value;
    const codeword = document.getElementById('decryptCodeword').value;
    
    if (!codeword) {
        alert('Please enter the codeword.');
        return;
    }
    
    confirmDecryptBtn.disabled = true;
    confirmDecryptBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Decrypting...';
    
    const formData = new FormData();
    formData.append('codeword', codeword);
    
    fetch(`/decrypt_file/${fileId}`, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            decryptModal.hide();
            
            const a = document.createElement('a');
            a.href = data.download_url;
            a.download = '';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            
            alert('File decrypted successfully! Download started.');
        } else {
            alert('Error: ' + data.message);
        }
        
        confirmDecryptBtn.disabled = false;
        confirmDecryptBtn.innerHTML = '<i class="fas fa-unlock"></i> Decrypt & Download';
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred during decryption.');
        
        confirmDecryptBtn.disabled = false;
        confirmDecryptBtn.innerHTML = '<i class="fas fa-unlock"></i> Decrypt & Download';
    });
});

decryptForm.addEventListener('submit', function(e) {
    e.preventDefault();
    confirmDecryptBtn.click();
});
