function instituionFormSubmit(event) {
    event.preventDefault();

    const institutionName = document.getElementById('institutionName').value;
    const institutionLocation = document.getElementById('institutionLocation').value;
    const institutionDescription = document.getElementById('institutionDescription').value;
    const user_id = document.getElementById('user_id').value;

    const data = {
        name: institutionName,
        location: institutionLocation,
        description: institutionDescription,
        user_id: user_id
    };

    fetch('/api/institution', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
            // redirect to the institutions page
            window.location.href = '/institution';
        })
        .catch((error) => {
            console.error('Error:', error);
        });
}