function categoriesFormSubmit(event) {
    event.preventDefault();

    const categoryName = document.getElementById('categoriesName').value;
    const categoriesGroupId = document.getElementById('categoriesGroupId').value;
    const categoriesTypeId = document.getElementById('categoriesTypeId').value;
    const user_id = document.getElementById('user_id').value;


    const data = {
        name: categoryName,
        categories_group_id: categoriesGroupId,
        categories_type_id: categoriesTypeId,
        user_id: user_id

    };

    fetch('/api/categories', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
            // redirect to the categories page
            window.location.href = '/categories';
        })
        .catch((error) => {
            console.error('Error:', error);
        });
}