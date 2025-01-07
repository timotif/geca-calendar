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