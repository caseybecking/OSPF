// Transactions CSV Import Handler

let selectedFile = null;

// Get DOM elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('csvFile');
const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const fileSize = document.getElementById('fileSize');
const removeFileBtn = document.getElementById('removeFile');
const uploadBtn = document.getElementById('uploadBtn');
const progressBar = document.getElementById('progressBar');
const resultMessage = document.getElementById('resultMessage');

// Handle file selection via input
fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFile(e.target.files[0]);
    }
});

// Handle drag and drop
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');

    if (e.dataTransfer.files.length > 0) {
        const file = e.dataTransfer.files[0];
        if (file.name.endsWith('.csv')) {
            handleFile(file);
        } else {
            showError('Please upload a CSV file');
        }
    }
});

// Handle file selection
function handleFile(file) {
    if (!file.name.endsWith('.csv')) {
        showError('Please select a CSV file');
        return;
    }

    selectedFile = file;

    // Display file info
    fileName.textContent = file.name;
    fileSize.textContent = formatFileSize(file.size);

    // Hide upload area, show file info
    uploadArea.style.display = 'none';
    fileInfo.style.display = 'block';
    resultMessage.style.display = 'none';
}

// Remove selected file
removeFileBtn.addEventListener('click', () => {
    selectedFile = null;
    fileInput.value = '';
    uploadArea.style.display = 'block';
    fileInfo.style.display = 'none';
    resultMessage.style.display = 'none';
});

// Upload and process file
uploadBtn.addEventListener('click', async () => {
    if (!selectedFile) {
        showError('No file selected');
        return;
    }

    // Show progress bar
    fileInfo.style.display = 'none';
    progressBar.style.display = 'block';
    resultMessage.style.display = 'none';

    // Create FormData
    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
        const response = await fetch('/api/transaction/csv_import', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        // Hide progress bar
        progressBar.style.display = 'none';
        resultMessage.style.display = 'block';

        if (response.ok || response.status === 201) {
            showSuccess(data);
        } else {
            showError(data.message || 'Upload failed');
        }

    } catch (error) {
        progressBar.style.display = 'none';
        resultMessage.style.display = 'block';
        showError('Error uploading file: ' + error.message);
    }
});

// Show success message
function showSuccess(data) {
    let errorDetailsHtml = '';
    if (data.error_details && data.error_details.length > 0) {
        let errorSummaryHtml = '';
        if (data.error_summary) {
            errorSummaryHtml = `
                <div class="mb-3">
                    <strong>Error Summary:</strong>
                    <ul>
                        ${Object.entries(data.error_summary).map(([type, count]) =>
                            `<li>${type.replace(/_/g, ' ')}: ${count}</li>`
                        ).join('')}
                    </ul>
                </div>
            `;
        }

        errorDetailsHtml = `
            <hr>
            <div class="alert alert-warning">
                <h6 class="alert-heading">Import Errors (showing first 50):</h6>
                ${errorSummaryHtml}
                <div style="max-height: 300px; overflow-y: auto;">
                    <ul class="mb-0">
                        ${data.error_details.map(err => `<li><small>${err}</small></li>`).join('')}
                    </ul>
                </div>
            </div>
        `;
    }

    const statusClass = data.transactions_created > 0 ? 'alert-success' : 'alert-warning';
    const statusIcon = data.transactions_created > 0 ? 'ri-checkbox-circle-line' : 'ri-error-warning-line';

    resultMessage.innerHTML = `
        <div class="alert ${statusClass} alert-dismissible fade show" role="alert">
            <h5 class="alert-heading"><i class="${statusIcon}"></i> Import Completed!</h5>
            <hr>
            <div class="row">
                <div class="col-md-4">
                    <div class="text-center">
                        <h3 class="text-success">${data.transactions_created}</h3>
                        <p class="text-muted mb-0">Transactions Created</p>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="text-center">
                        <h3 class="text-info">${data.transactions_skipped}</h3>
                        <p class="text-muted mb-0">Duplicates Skipped</p>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="text-center">
                        <h3 class="${data.errors > 0 ? 'text-danger' : 'text-muted'}">${data.errors}</h3>
                        <p class="text-muted mb-0">Errors</p>
                    </div>
                </div>
            </div>
            ${errorDetailsHtml}
            <hr>
            <div class="mt-3">
                <a href="/transactions" class="btn btn-primary">
                    <i class="ri-eye-line"></i> View Transactions
                </a>
                <button class="btn btn-outline-primary" onclick="location.reload()">
                    <i class="ri-upload-2-line"></i> Import Another File
                </button>
            </div>
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
}

// Show error message
function showError(message) {
    resultMessage.innerHTML = `
        <div class="alert alert-danger alert-dismissible fade show" role="alert">
            <h5 class="alert-heading"><i class="ri-error-warning-line"></i> Import Failed</h5>
            <p class="mb-0">${message}</p>
            <hr>
            <div class="mt-2">
                <p class="mb-2"><strong>Common Issues:</strong></p>
                <ul class="mb-0">
                    <li>Categories must already exist - import categories first</li>
                    <li>Check that your CSV has the required headers</li>
                    <li>Verify date format is MM/DD/YYYY or YYYY-MM-DD</li>
                    <li>Ensure amounts are in valid format ($100.50 or -50.00)</li>
                </ul>
            </div>
            <hr>
            <button class="btn btn-outline-danger" onclick="location.reload()">
                <i class="ri-refresh-line"></i> Try Again
            </button>
            <a href="/categories/import" class="btn btn-outline-primary">
                <i class="ri-upload-line"></i> Import Categories First
            </a>
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
}

// Format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}
