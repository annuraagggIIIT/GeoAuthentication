document.getElementById('detect-country').addEventListener('click', function() {
    fetch('/get_real_country')
        .then(response => response.json())
        .then(data => {
            document.getElementById('real-country').textContent = 'Your real country is: ' + data.real_country;
        })
        .catch(error => {
            document.getElementById('real-country').textContent = 'Error detecting location';
            console.error('Error:', error);
        });
});
