// Categories CSV Import Handler

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
        const response = await fetch('/api/categories/csv_import', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        // Hide progress bar
        progressBar.style.display = 'none';
        resultMessage.style.display = 'block';

        if (response.ok) {
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
    resultMessage.innerHTML = `
        <div class="alert alert-success alert-dismissible fade show" role="alert">
            <h5 class="alert-heading"><i class="ri-checkbox-circle-line"></i> Import Successful!</h5>
            <hr>
            <div class="row">
                <div class="col-md-3">
                    <div class="text-center">
                        <h3 class="text-success">${data.categories_created}</h3>
                        <p class="text-muted mb-0">Categories Created</p>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="text-center">
                        <h3 class="text-info">${data.categories_skipped}</h3>
                        <p class="text-muted mb-0">Duplicates Skipped</p>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="text-center">
                        <h3 class="text-primary">${data.groups_processed}</h3>
                        <p class="text-muted mb-0">Groups Processed</p>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="text-center">
                        <h3 class="text-primary">${data.types_processed}</h3>
                        <p class="text-muted mb-0">Types Processed</p>
                    </div>
                </div>
            </div>
            <hr>
            <div class="mt-3">
                <a href="/categories" class="btn btn-primary">
                    <i class="ri-eye-line"></i> View Categories
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
            <button class="btn btn-outline-danger" onclick="location.reload()">
                <i class="ri-refresh-line"></i> Try Again
            </button>
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
