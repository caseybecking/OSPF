function groupsFormSubmit(event) {
    event.preventDefault();

    const groupName = document.getElementById('categoryGroupName').value;
    const user_id = document.getElementById('user_id').value;

    const data = {
        name: groupName,
        user_id: user_id
    };

    fetch('/api/categories_group', {
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
            window.location.href = '/categories/group';
        })
        .catch((error) => {
            console.error('Error:', error);
        });
}