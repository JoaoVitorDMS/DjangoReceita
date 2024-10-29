const darkModeToggle = document.getElementById('dark-mode-toggle');
const increaseFont = document.getElementById('increase-font');
const decreaseFont = document.getElementById('decrease-font');

darkModeToggle.addEventListener('click', () => {
    document.body.classList.toggle('dark-mode');
    const elements = document.querySelectorAll('.navbar, .btn-outline-light');
    elements.forEach(element => {
        element.classList.toggle('dark-mode');
    });
});

increaseFont.addEventListener('click', () => {
    document.body.style.fontSize = 'larger';
});

decreaseFont.addEventListener('click', () => {
    document.body.style.fontSize = 'smaller';
});
