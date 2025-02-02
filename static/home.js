document.addEventListener("DOMContentLoaded", function () {
    const uploadedarea = document.getElementById('upload1');
    const inputimage = document.getElementById('file1');
    const imagepreview = document.getElementById('preview1');
    const textupload = uploadedarea.querySelector('p');
    const resultsarea = document.getElementById('results');
    const form = document.getElementById('uploadForm');

    //when clicked on it will trigger the hidden input image
    uploadedarea.addEventListener('click', () => {
        //when clicked it will trigger the file input
        inputimage.click();
    });

    //an event listener for when an image is clicked
    inputimage.addEventListener('change', (event) => {
        const file = event.target.files[0];
        if (file) {
            //get the file to be read
            const reader = new FileReader();

            //when the file is read then update the preview image
            reader.onload = () => {
                //display the image in the preview area and make it visible
                imagepreview.src = reader.result;
                imagepreview.hidden = false;
                textupload.hidden = true;
            };

            //read the file as a data URL
            reader.readAsDataURL(file);
        }
    });

    //when the form is submitted
    form.addEventListener('submit', async (e) => {
        //prevent the form from submitting
        e.preventDefault();
        //display loading message while waiting for the response
        resultsarea.innerHTML = '<p>Loading...</p>';
    
        //create a new form data object
        const formdata = new FormData(form);

        try {
            //connects to views.py send post request to the root url
            const response = await fetch('/', { 
                method: 'POST',
                //send the form data as the body of the request
                body: formdata,
            });
    
            if (response.ok) {
                //recieve the data from the response
                const data = await response.json();
                //recieve the data from views.py
                const { predicted_breed, confidence, facts, image_url } = data;
    
                //display the results in the html template
                //display the image, predicted breed, confidence and facts
                resultsarea.innerHTML = `
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
                //display an error message if the request failed
                const error = await response.json();
                resultsarea.innerHTML = `<p style="color: red;">${error.error || 'Error processing the image.'}</p>`;
            }
            //handle any errors that occur
        } catch (error) {
            console.error('Error:', error);
            resultsarea.innerHTML = '<p style="color: red;">An error occurred. Please try again later.</p>';
        }
    });
});