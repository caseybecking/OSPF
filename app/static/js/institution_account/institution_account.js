function instituionAccountFormSubmit(event) {
    event.preventDefault();

    const institutionId = document.getElementById('instituionId').value;
    const accountName = document.getElementById('accountName').value;
    const accountNumber = document.getElementById('accountNumber').value;
    const accountStatus = document.getElementById('accountStatus').value;
    const user_id = document.getElementById('user_id').value;

    const data = {
        institution_id: institutionId,
        name: accountName,
        number: accountNumber,
        status: accountStatus,
        user_id: user_id,
        balance: 0,
        starting_balance: 0,
        account_type: 'checking',
        account_class: 'asset'
    };

    fetch('/api/institution/account', {
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
            window.location.href = '/account';
        })
        .catch((error) => {
            console.error('Error:', error);
        });

}

async function editAccount(accountId) {
    // Fetch the account data
    try {
        const response = await fetch(`/api/institution/account/${accountId}`);
        const data = await response.json();

        if (response.ok) {
            // Populate the edit form
            document.getElementById('edit_account_id').value = accountId;
            document.getElementById('edit_accountName').value = data.account.name;
            document.getElementById('edit_accountNumber').value = data.account.number || '';
            document.getElementById('edit_accountStatus').value = data.account.status || '';
            document.getElementById('edit_instituionId').value = data.account.institution_id || '';

            // Show the modal
            const editModal = new bootstrap.Modal(document.getElementById('EditAccountModal'));
            editModal.show();
        } else {
            alert('Error loading account: ' + data.message);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error loading account');
    }
}

function updateAccount(event) {
    event.preventDefault();

    const accountId = document.getElementById('edit_account_id').value;
    const institutionId = document.getElementById('edit_instituionId').value;
    const accountName = document.getElementById('edit_accountName').value;
    const accountNumber = document.getElementById('edit_accountNumber').value;
    const accountStatus = document.getElementById('edit_accountStatus').value;
    const user_id = document.getElementById('edit_account_user_id').value;

    const data = {
        institution_id: institutionId,
        name: accountName,
        number: accountNumber,
        status: accountStatus,
        user_id: user_id,
        balance: 0,
        starting_balance: 0,
        account_type: 'checking',
        account_class: 'asset'
    };

    fetch(`/api/institution/account/${accountId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
            // redirect to the accounts page
            window.location.href = '/account';
        })
        .catch((error) => {
            console.error('Error:', error);
            alert('Error updating account');
        });
}

async function deleteAccount(accountId) {
    if (!confirm('Are you sure you want to delete this account?')) {
        return;
    }

    try {
        const response = await fetch(`/api/institution/account/${accountId}`, {
            method: 'DELETE',
        });

        const data = await response.json();

        if (response.ok) {
            alert('Account deleted successfully');
            window.location.href = '/account';
        } else {
            alert('Error deleting account: ' + data.message);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error deleting account');
    }
}