document.addEventListener("DOMContentLoaded", function () {
    const uploadArea = document.getElementById('upload1');
    const fileInput = document.getElementById('file1');
    const previewImage = document.getElementById('preview1');
    const uploadText = uploadArea.querySelector('p');
    const resultsDiv = document.getElementById('results');
    const form = document.getElementById('uploadForm');

    // Open file dialog when clicking on the upload area
    uploadArea.addEventListener('click', () => {
        fileInput.click();
    });

    // Handle file selection
    fileInput.addEventListener('change', (event) => {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();

            // When file is read, update the preview image
            reader.onload = () => {
                previewImage.src = reader.result;
                previewImage.hidden = false;
                uploadText.hidden = true;
            };

            reader.readAsDataURL(file);
        }
    });

    // Handle form submission and display results
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        resultsDiv.innerHTML = '<p>Loading...</p>';
    
        const formData = new FormData(form);
        try {
            const response = await fetch('/', { // Ensure this is the correct endpoint
                method: 'POST',
                body: formData,
            });
    
            if (response.ok) {
                const data = await response.json();
                const { predicted_breed, confidence, facts, image_url } = data;
    
                resultsDiv.innerHTML = `
                    <h2>Prediction Results</h2>
                    <img src="${image_url}" alt="Uploaded Image" style="max-width: 300px;">
                    <h3>Predicted Breed: ${predicted_breed}</h3>
                    <h3>Confidence: ${confidence.toFixed(2)}%</h3>
                    <h3>Facts:</h3>
                    <ul>
                        <li>Length: ${facts.Length || "Unknown"}</li>
                        <li>Children Friendly: ${facts["Children Friendly"] || "Unknown"}</li>
                        <li>General Health: ${facts["General Health"] || "Unknown"}</li>
                    </ul>
                `;
            } else {
                const error = await response.json();
                resultsDiv.innerHTML = `<p style="color: red;">${error.error || 'Error processing the image.'}</p>`;
            }
        } catch (error) {
            console.error('Error:', error);
            resultsDiv.innerHTML = '<p style="color: red;">An error occurred. Please try again later.</p>';
        }
    });
});