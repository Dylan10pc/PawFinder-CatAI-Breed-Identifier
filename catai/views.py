from django.shortcuts import render
import os
import numpy as np
import pandas as pd
from django.shortcuts import render
from django.conf import settings
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from .forms import CatImageUploadForm
from django.http import JsonResponse
# Create your views here.
def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')


# Load model and CSV
MODEL_PATH = os.path.join(settings.BASE_DIR, "catbreedmodel1.keras")
CSV_PATH = os.path.join(settings.BASE_DIR, "cat_breeds.csv")
model = load_model(MODEL_PATH)
breed_info = pd.read_csv(CSV_PATH).set_index("name")

# Map class indices to breed names
class_indices = {i: breed for i, breed in enumerate(breed_info.index)}

def predict_cat_breed(image_path):
    try:
        # Preprocess the image
        img = load_img(image_path, target_size=(224, 224))
        img_array = img_to_array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        # Predict the breed
        predictions = model.predict(img_array)
        confidence = np.max(predictions) * 100
        predicted_index = np.argmax(predictions)
        predicted_breed = class_indices[predicted_index]

        # Get breed details
        breed_details = breed_info.loc[predicted_breed]
        facts = {
            "Length": breed_details.get("length", "Unknown"),
            "Children Friendly": breed_details.get("children_friendly", "Unknown"),
            "General Health": breed_details.get("general_health", "Unknown"),
        }
        return predicted_breed, confidence, facts

    except Exception as e:
        # Log the error (optional)
        print(f"Prediction error: {e}")
        return "Unknown", 0, {}
def home(request):
    if request.method == "POST":
        form = CatImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.cleaned_data["image"]

            # Validate file extension
            if not image.name.lower().endswith(('.png', '.jpg', '.jpeg')):
                return JsonResponse({"error": "Only PNG, JPG, or JPEG files are supported."}, status=400)

            # Save the uploaded image
            upload_dir = os.path.join(settings.MEDIA_ROOT, "uploads")
            os.makedirs(upload_dir, exist_ok=True)  # Ensure the directory exists
            image_path = os.path.join(upload_dir, image.name)

            with open(image_path, "wb+") as f:
                for chunk in image.chunks():
                    f.write(chunk)

            # Make predictions
            predicted_breed, confidence, facts = predict_cat_breed(image_path)

            # Ensure all values are JSON serializable
            response_data = {
    "predicted_breed": predicted_breed,
    "confidence": float(confidence),
    "facts": {k: (int(v) if isinstance(v, (np.integer, np.int64)) else v) for k, v in facts.items()},
    "image_url": os.path.join(settings.MEDIA_URL, "uploads", image.name),
}
            return JsonResponse(response_data)

        return JsonResponse({"error": "Invalid form submission."}, status=400)

    # Render the page for GET requests
    return render(request, "home.html", {"form": CatImageUploadForm()})