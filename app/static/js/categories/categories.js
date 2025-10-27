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

async function editCategory(categoryId) {
    // Fetch the category data
    try {
        const response = await fetch(`/api/categories/${categoryId}`);
        const data = await response.json();

        if (response.ok) {
            // Populate the edit form
            document.getElementById('edit_category_id').value = categoryId;
            document.getElementById('edit_categoriesName').value = data.category.name;
            document.getElementById('edit_categoriesGroupId').value = data.category.categories_group_id || '';
            document.getElementById('edit_categoriesTypeId').value = data.category.categories_type_id || '';

            // Show the modal
            const editModal = new bootstrap.Modal(document.getElementById('EditCategoryModal'));
            editModal.show();
        } else {
            alert('Error loading category: ' + data.message);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error loading category');
    }
}

function updateCategory(event) {
    event.preventDefault();

    const categoryId = document.getElementById('edit_category_id').value;
    const categoryName = document.getElementById('edit_categoriesName').value;
    const categoriesGroupId = document.getElementById('edit_categoriesGroupId').value;
    const categoriesTypeId = document.getElementById('edit_categoriesTypeId').value;
    const user_id = document.getElementById('edit_category_user_id').value;

    const data = {
        name: categoryName,
        categories_group_id: categoriesGroupId,
        categories_type_id: categoriesTypeId,
        user_id: user_id
    };

    fetch(`/api/categories/${categoryId}`, {
        method: 'PUT',
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
            alert('Error updating category');
        });
}

async function deleteCategory(categoryId) {
    if (!confirm('Are you sure you want to delete this category?')) {
        return;
    }

    try {
        const response = await fetch(`/api/categories/${categoryId}`, {
            method: 'DELETE',
        });

        const data = await response.json();

        if (response.ok) {
            alert('Category deleted successfully');
            window.location.href = '/categories';
        } else {
            alert('Error deleting category: ' + data.message);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error deleting category');
    }
}