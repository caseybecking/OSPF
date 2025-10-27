var previewTemplate, dropzone, dropzonePreviewNode, inputMultipleElements;

// Configure Dropzone
dropzonePreviewNode = document.querySelector("#dropzone-preview-list");
if (dropzonePreviewNode) {
    dropzonePreviewNode.id = "";
    previewTemplate = dropzonePreviewNode.parentNode.innerHTML;
    dropzonePreviewNode.parentNode.removeChild(dropzonePreviewNode);
    dropzone = new Dropzone(".dropzone", {
        url: "/api/transaction/csv_import", // Initial URL for Dropzone
        method: "post",
        previewTemplate: previewTemplate,
        previewsContainer: "#dropzone-preview",
        autoProcessQueue: false, // Prevent auto processing
        init: function () {
            this.on("addedfile", function (file) {
                console.log("File added: ", file);
            });
            this.on("sending", function (file, xhr, formData) {
                formData.append("upload_purpose", "okta_processing");
            });
            this.on("success", function (file, response) {
                dropzone.removeFile(file);
                console.log("Successfully uploaded:", response);
            });
            this.on("error", function (file, errorMessage) {
                console.error("Failed to upload:", errorMessage);
            });
        }
    });
}

// Function to handle CSV upload and send it to the API endpoint
function uploadCSV(file) {
    var formData = new FormData();
    formData.append("file", file);

    fetch("/api/transaction/csv_import", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        console.log("Successfully processed:", data);
        //# TODO: add a modal saying it has been processed 
        dropzone.removeFile(file);
    })
    .catch(error => {
        console.error("Error uploading CSV:", error);
    });
}

// Wait until the DOM is fully loaded before adding event listener
document.addEventListener("DOMContentLoaded", function () {
    var uploadButton = document.querySelector("#upload-button");
    if (uploadButton) {
        uploadButton.addEventListener("click", function () {
            console.log("Upload button clicked.");
            if (dropzone.getAcceptedFiles().length > 0) {
                dropzone.getAcceptedFiles().forEach(function (file) {
                    uploadCSV(file);
                });
            } else {
                alert("Please add a file to upload.");
            }
        });
    } else {
        console.error("Upload button not found.");
    }
});

// Transaction CRUD functions
function transactionsFormSubmit(event) {
    event.preventDefault();
    const description = document.getElementById('transactionDescription').value;
    const user_id = document.getElementById('user_id').value;

    // For now, this is a simplified version - you may want to add more fields
    alert('Transaction creation form needs more fields. Please use CSV import instead.');
}

async function editTransaction(transactionId) {
    // Fetch the transaction data
    try {
        const response = await fetch(`/api/transaction/${transactionId}`);
        const data = await response.json();

        if (response.ok) {
            // Populate the edit form
            document.getElementById('edit_transaction_id').value = transactionId;
            document.getElementById('edit_transactionMerchant').value = data.transaction.merchant || '';
            document.getElementById('edit_transactionOriginalStatement').value = data.transaction.original_statement || '';
            document.getElementById('edit_transactionNotes').value = data.transaction.notes || '';
            document.getElementById('edit_transactionTags').value = data.transaction.tags || '';
            document.getElementById('edit_transactionDescription').value = data.transaction.description || '';
            document.getElementById('edit_transactionAmount').value = data.transaction.amount || '';
            document.getElementById('edit_transactionCategory').value = data.transaction.categories_id || '';
            document.getElementById('edit_transactionAccount').value = data.transaction.account_id || '';

            // Show the modal
            const editModal = new bootstrap.Modal(document.getElementById('EditTransactionModal'));
            editModal.show();
        } else {
            alert('Error loading transaction: ' + data.message);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error loading transaction');
    }
}

function updateTransaction(event) {
    event.preventDefault();

    const transactionId = document.getElementById('edit_transaction_id').value;
    const merchant = document.getElementById('edit_transactionMerchant').value;
    const originalStatement = document.getElementById('edit_transactionOriginalStatement').value;
    const notes = document.getElementById('edit_transactionNotes').value;
    const tags = document.getElementById('edit_transactionTags').value;
    const description = document.getElementById('edit_transactionDescription').value;
    const amount = document.getElementById('edit_transactionAmount').value;
    const categoryId = document.getElementById('edit_transactionCategory').value;
    const accountId = document.getElementById('edit_transactionAccount').value;
    const user_id = document.getElementById('edit_transaction_user_id').value;

    const data = {
        merchant: merchant,
        original_statement: originalStatement,
        notes: notes,
        tags: tags,
        description: description,
        amount: parseFloat(amount),
        categories_id: categoryId,
        account_id: accountId,
        user_id: user_id
    };

    fetch(`/api/transaction/${transactionId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
            // redirect to the transactions page
            window.location.href = '/transactions';
        })
        .catch((error) => {
            console.error('Error:', error);
            alert('Error updating transaction');
        });
}

async function deleteTransaction(transactionId) {
    if (!confirm('Are you sure you want to delete this transaction?')) {
        return;
    }

    try {
        const response = await fetch(`/api/transaction/${transactionId}`, {
            method: 'DELETE',
        });

        const data = await response.json();

        if (response.ok) {
            alert('Transaction deleted successfully');
            window.location.href = '/transactions';
        } else {
            alert('Error deleting transaction: ' + data.message);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error deleting transaction');
    }
}
