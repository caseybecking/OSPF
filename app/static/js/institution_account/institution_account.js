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