from django.shortcuts import render
import os
import numpy as np
import pandas as pd
from django.shortcuts import render
from django.conf import settings
import tensorflow as tf
tf.config.set_visible_devices([], 'GPU')
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from .forms import catimageformforupload
from django.http import JsonResponse
# Create your views here.

#these are paths to the model and csv file
pathtomodel = os.path.join(settings.BASE_DIR, "catbreedmodel1.keras")
pathtocsv = os.path.join(settings.BASE_DIR, "cat_breeds.csv")
#load the model 
model = load_model(pathtomodel)
#read breed info from csv file and sets breed name as the index
breedinfos = pd.read_csv(pathtocsv).set_index("name")

#create a mapping from model output index to breed name
class_indices = {i: breed for i, breed in enumerate(breedinfos.index)}

#view for the about page
def about(request):
    return render(request, 'about.html')

#a function to predict the breed of a cat from an image
def predictcatbreed(image_path):
    try:
        #load the image and preprocess it
        #resizes image then converts it to an array
        #expands the dimensions of the array
        img = load_img(image_path, target_size=(224, 224))
        imgarray = img_to_array(img) / 255.0
        imgarray = np.expand_dims(imgarray, axis=0)

        #make a prediction with the model 
        predictions = model.predict(imgarray)
        #confidence prediction and get the index of the highest confidence
        confidence = np.max(predictions) * 100
        #get the index of the highest confidence prediction
        predictedindex = np.argmax(predictions)
        #get the breed name from the index
        predictedbreedname = class_indices[predictedindex]

        #get the breed details from the csv file
        breed_details = breedinfos.loc[predictedbreedname]
        facts = {
            "Length": breed_details.get("length", "Unknown"),
            "Children Friendly": breed_details.get("children_friendly", "Unknown"),
            "General Health": breed_details.get("general_health", "Unknown"),
        }
        #return the predicted breed name, confidence and facts
        return predictedbreedname, confidence, facts

    #if there is an error print the error
    except Exception as e:
        print(f"Prediction error: {e}")
        return "Unknown", 0, {}
    
#home view that handles the image and predictions
def home(request):
    #if the request is a post request
    if request.method == "POST":
        #get the image from the form
        form = catimageformforupload(request.POST, request.FILES)
        if form.is_valid():
            #get the image from the form
            imagefromform = form.cleaned_data["image"]

            #check if the image is a png, jpg or jpeg file and if not return an error
            if not imagefromform.name.lower().endswith(('.png', '.jpg', '.jpeg')):
                return JsonResponse({"error": "Only PNG, JPG, or JPEG files are supported."}, status=400)

            #save the image to the uploads directory and get the full path of the image
            dirupload = os.path.join(settings.MEDIA_ROOT, "uploads")
            os.makedirs(dirupload, exist_ok=True) 
            #save the image to the uploads directory
            pathtoimage = os.path.join(dirupload, imagefromform.name)
            with open(pathtoimage, "wb+") as f:
                for chunk in imagefromform.chunks():
                    f.write(chunk)

            #predict the breed of the cat from the image
            predictedbreed, confidence, facts = predictcatbreed(pathtoimage)

            #this is the prediction of the cat response 
            dataresponse = {
                #predicted breed
                "predicted_breed": predictedbreed,
                #confidence of the prediction
                "confidence": float(confidence),
                #facts about the breed turn and convert the facts to integers and run a for loop to get the facts
                "facts": {k: (int(v) if isinstance(v, (np.integer, np.int64)) else v) for k, v in facts.items()},
                #image url of the image
                "image_url": os.path.join(settings.MEDIA_URL, "uploads", imagefromform.name),
            }
            #return the prediction of the cat response as a json response
            return JsonResponse(dataresponse)
        #if the form is invalid return an error
        return JsonResponse({"error": "Invalid form submission."}, status=400)
    #render the home page with the form
    return render(request, "home.html", {"form": catimageformforupload()})