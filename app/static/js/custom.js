document.addEventListener('DOMContentLoaded', async () => {
    // Auto download calendar
    const filename = document.getElementById('calendar-url').value;
    const a = document.createElement('a');
    a.href = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
});

function copyUrl() {
    const urlInput = document.getElementById('calendar-url');
    urlInput.select();
    document.execCommand('copy');
    
    const button = document.getElementById('copy-button');
    button.textContent = 'Copied!';
    button.classList.add('btn-success');
    
    setTimeout(() => {
        button.textContent = 'Copy URL';
        button.classList.remove('btn-success');
    }, 2000);
}