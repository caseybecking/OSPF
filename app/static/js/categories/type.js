function typesFormSubmit(event) {
    event.preventDefault();

    const typeName = document.getElementById('categoryTypeName').value;
    const user_id = document.getElementById('user_id').value;

    const data = {
        name: typeName,
        user_id: user_id
    };

    fetch('/api/categories_type', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
            // redirect to the types page
            window.location.href = '/categories/type';
        })
        .catch((error) => {
            console.error('Error:', error);
        });
}