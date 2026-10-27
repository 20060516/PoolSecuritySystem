import os
import json
import time

import cv2
import numpy as np
import tensorflow as tf


class MLService:

    def __init__(self, model_path, class_mapping_path=None):

        print("----------------------------------------")
        print("Loading CNN model...")
        print("Model:", model_path)

        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Model file not found: {model_path}"
            )

        # Load trained CNN model
        self.model = tf.keras.models.load_model(model_path)

        print("CNN model loaded successfully.")

        # Default class mapping
        self.class_names = {
            0: "DROWNING",
            1: "NON-DROWNING"
        }

        # Load saved class mapping if available
        if class_mapping_path and os.path.exists(class_mapping_path):

            try:
                with open(class_mapping_path, "r") as file:
                    class_indices = json.load(file)

                # Example:
                # {"Drowning": 0, "Non Drowning": 1}

                self.class_names = {
                    int(index): name.upper().replace(" ", "-")
                    for name, index in class_indices.items()
                }

                print("Class mapping:", self.class_names)

            except Exception as e:
                print("Warning: Could not load class mapping.")
                print(e)

        print("----------------------------------------")


    def predict_frame(self, frame):

        # Record inference start time
        start_time = time.perf_counter()

        # -----------------------------------------
        # Resize frame
        # -----------------------------------------

        image = cv2.resize(
            frame,
            (224, 224)
        )

        # -----------------------------------------
        # Convert BGR → RGB
        # -----------------------------------------

        image = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2RGB
        )

        # -----------------------------------------
        # Normalize pixel values
        # -----------------------------------------

        image = image.astype(
            np.float32
        ) / 255.0

        # -----------------------------------------
        # Add batch dimension
        # -----------------------------------------

        image = np.expand_dims(
            image,
            axis=0
        )

        # -----------------------------------------
        # CNN prediction
        # -----------------------------------------

        predictions = self.model.predict(
            image,
            verbose=0
        )

        # -----------------------------------------
        # Get predicted class
        # -----------------------------------------

        predicted_index = int(
            np.argmax(predictions[0])
        )

        confidence = float(
            predictions[0][predicted_index]
        )

        label = self.class_names.get(
            predicted_index,
            "UNKNOWN"
        )

        # -----------------------------------------
        # Calculate inference time
        # -----------------------------------------

        inference_time = (
            time.perf_counter() - start_time
        ) * 1000

        # -----------------------------------------
        # Return prediction data
        # -----------------------------------------

        return {
            "label": label,
            "class_index": predicted_index,
            "confidence": confidence,
            "confidence_percent": round(
                confidence * 100,
                2
            ),
            "inference_ms": round(
                inference_time,
                2
            )
        }