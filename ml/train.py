import os
import json

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import (
    Conv2D,
    MaxPooling2D,
    Dropout,
    Flatten,
    Dense
)
from tensorflow.keras.preprocessing.image import ImageDataGenerator


# =========================================================
# PROJECT PATHS
# =========================================================

PROJECT_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

TRAIN_DIR = os.path.join(
    PROJECT_DIR,
    "ml",
    "dataset",
    "train"
)

VAL_DIR = os.path.join(
    PROJECT_DIR,
    "ml",
    "dataset",
    "val"
)

MODEL_DIR = os.path.join(
    PROJECT_DIR,
    "backend",
    "model"
)

os.makedirs(MODEL_DIR, exist_ok=True)


# =========================================================
# TRAINING SETTINGS
# =========================================================

IMAGE_SIZE = (224, 224)
BATCH_SIZE = 15
EPOCHS = 10


print("----------------------------------------")
print("AquaGuard CNN Model Training")
print("----------------------------------------")

print("Training dataset:")
print(TRAIN_DIR)

print("Validation dataset:")
print(VAL_DIR)

print("----------------------------------------")


# =========================================================
# CHECK DATASET
# =========================================================

if not os.path.exists(TRAIN_DIR):
    raise FileNotFoundError(
        f"Training folder not found: {TRAIN_DIR}"
    )

if not os.path.exists(VAL_DIR):
    raise FileNotFoundError(
        f"Validation folder not found: {VAL_DIR}"
    )


# =========================================================
# IMAGE DATA GENERATORS
# =========================================================

train_datagen = ImageDataGenerator(
    rescale=1.0 / 255.0,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True
)

validation_datagen = ImageDataGenerator(
    rescale=1.0 / 255.0
)


train_generator = train_datagen.flow_from_directory(
    TRAIN_DIR,
    target_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    class_mode="categorical",
    shuffle=True
)


validation_generator = validation_datagen.flow_from_directory(
    VAL_DIR,
    target_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    class_mode="categorical",
    shuffle=False
)


# =========================================================
# DISPLAY CLASS INFORMATION
# =========================================================

print("----------------------------------------")
print("Class mapping:")
print(train_generator.class_indices)
print("----------------------------------------")

print(
    f"Training images: {train_generator.samples}"
)

print(
    f"Validation images: {validation_generator.samples}"
)

print("----------------------------------------")


# =========================================================
# CNN MODEL
# =========================================================

model = Sequential([

    Conv2D(
        32,
        (3, 3),
        activation="relu",
        input_shape=(224, 224, 3)
    ),

    MaxPooling2D(
        pool_size=(2, 2)
    ),

    Conv2D(
        64,
        (3, 3),
        activation="relu"
    ),

    MaxPooling2D(
        pool_size=(2, 2)
    ),

    Dropout(0.25),

    Flatten(),

    Dense(
        256,
        activation="relu"
    ),

    Dropout(0.5),

    Dense(
        512,
        activation="relu"
    ),

    Dropout(0.5),

    Dense(
        2,
        activation="softmax"
    )
])


# =========================================================
# COMPILE MODEL
# =========================================================

model.compile(
    optimizer="adam",
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)


# =========================================================
# DISPLAY MODEL
# =========================================================

print("----------------------------------------")
print("CNN Model Summary")
print("----------------------------------------")

model.summary()


# =========================================================
# TRAIN MODEL
# =========================================================

print("----------------------------------------")
print("Starting CNN training...")
print("----------------------------------------")

history = model.fit(
    train_generator,
    validation_data=validation_generator,
    epochs=EPOCHS
)


# =========================================================
# SAVE MODEL
# =========================================================

model_path = os.path.join(
    MODEL_DIR,
    "trained_model.h5"
)

model.save(model_path)


# =========================================================
# SAVE CLASS MAPPING
# =========================================================

class_mapping_path = os.path.join(
    MODEL_DIR,
    "class_indices.json"
)

with open(
    class_mapping_path,
    "w"
) as file:

    json.dump(
        train_generator.class_indices,
        file,
        indent=4
    )


# =========================================================
# SAVE TRAINING HISTORY
# =========================================================

history_path = os.path.join(
    MODEL_DIR,
    "training_history.json"
)

history_data = {
    key: [float(value) for value in values]
    for key, values in history.history.items()
}

with open(
    history_path,
    "w"
) as file:

    json.dump(
        history_data,
        file,
        indent=4
    )


# =========================================================
# FINAL OUTPUT
# =========================================================

print("----------------------------------------")
print("TRAINING COMPLETED")
print("----------------------------------------")

print("Model saved at:")
print(model_path)

print("Class mapping saved at:")
print(class_mapping_path)

print("Training history saved at:")
print(history_path)

print("----------------------------------------")
print("AquaGuard CNN model is ready.")
print("----------------------------------------")