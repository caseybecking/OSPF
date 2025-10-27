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

async function editInstitution(institutionId) {
    // Fetch the institution data
    try {
        const response = await fetch(`/api/institution/${institutionId}`);
        const data = await response.json();

        if (response.ok) {
            // Populate the edit form
            document.getElementById('edit_institution_id').value = institutionId;
            document.getElementById('edit_institutionName').value = data.institution.name;
            document.getElementById('edit_institutionLocation').value = data.institution.location || '';
            document.getElementById('edit_institutionDescription').value = data.institution.description || '';

            // Show the modal
            const editModal = new bootstrap.Modal(document.getElementById('EditInstitutionModal'));
            editModal.show();
        } else {
            alert('Error loading institution: ' + data.message);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error loading institution');
    }
}

function updateInstitution(event) {
    event.preventDefault();

    const institutionId = document.getElementById('edit_institution_id').value;
    const institutionName = document.getElementById('edit_institutionName').value;
    const institutionLocation = document.getElementById('edit_institutionLocation').value;
    const institutionDescription = document.getElementById('edit_institutionDescription').value;
    const user_id = document.getElementById('edit_user_id').value;

    const data = {
        name: institutionName,
        location: institutionLocation,
        description: institutionDescription,
        user_id: user_id
    };

    fetch(`/api/institution/${institutionId}`, {
        method: 'PUT',
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
            alert('Error updating institution');
        });
}

async function deleteInstitution(institutionId) {
    if (!confirm('Are you sure you want to delete this institution?')) {
        return;
    }

    try {
        const response = await fetch(`/api/institution/${institutionId}`, {
            method: 'DELETE',
        });

        const data = await response.json();

        if (response.ok) {
            alert('Institution deleted successfully');
            window.location.href = '/institution';
        } else {
            alert('Error deleting institution: ' + data.message);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error deleting institution');
    }
}