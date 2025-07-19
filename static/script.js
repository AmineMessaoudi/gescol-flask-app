// script.js

document.addEventListener('DOMContentLoaded', function() {
    const timeElement = document.getElementById('current-time');

    function updateTime() {
        const now = new Date();
        const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit' };
        timeElement.textContent = now.toLocaleDateString('fr-FR', options);
    }

    if (timeElement) {
        updateTime(); // Initial call
        setInterval(updateTime, 1000); // Update every second
    }
});
