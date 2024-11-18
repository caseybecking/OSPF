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
