import os
import cv2
import numpy as np
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.optimizers import Adam
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt

# =============================
# Settings
# =============================
DATASET_PATH = "dataset"
REAL_PATH = os.path.join(DATASET_PATH, "videos_real")
FAKE_PATH = os.path.join(DATASET_PATH, "videos_fake")
IMG_SIZE = 224
FRAMES_PER_VIDEO = 5
EPOCHS = 10
BATCH_SIZE = 16

# =============================
# Extract frames from videos
# =============================
def extract_frames(video_path, label, frames_per_video=FRAMES_PER_VIDEO):
    frames = []
    cap = cv2.VideoCapture(video_path)
    length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    step = max(1, length // frames_per_video)

    for i in range(0, length, step):
        cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        success, frame = cap.read()
        if not success:
            continue
        frame = cv2.resize(frame, (IMG_SIZE, IMG_SIZE))
        frame = frame.astype("float32") / 255.0
        frames.append((frame, label))
        if len(frames) >= frames_per_video:
            break
    cap.release()
    return frames

print("📂 Loading dataset...")
X, y = [], []

# Real videos
for video in os.listdir(REAL_PATH):
    if video.endswith((".mp4", ".avi", ".mov")):
        frames = extract_frames(os.path.join(REAL_PATH, video), 0)
        for f, l in frames:
            X.append(f)
            y.append(l)

# Fake videos
for video in os.listdir(FAKE_PATH):
    if video.endswith((".mp4", ".avi", ".mov")):
        frames = extract_frames(os.path.join(FAKE_PATH, video), 1)
        for f, l in frames:
            X.append(f)
            y.append(l)

X = np.array(X)
y = np.array(y)

print(f"✅ Dataset loaded: {X.shape[0]} frames")

# =============================
# Train-test split
# =============================
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

# =============================
# Data augmentation
# =============================
datagen = ImageDataGenerator(
    rotation_range=10,
    width_shift_range=0.1,
    height_shift_range=0.1,
    horizontal_flip=True
)
datagen.fit(X_train)

# =============================
# Model (Transfer Learning - MobileNetV2)
# =============================
base_model = MobileNetV2(weights="imagenet", include_top=False, input_shape=(IMG_SIZE, IMG_SIZE, 3))
x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dropout(0.3)(x)
x = Dense(128, activation="relu")(x)
predictions = Dense(1, activation="sigmoid")(x)

model = Model(inputs=base_model.input, outputs=predictions)

for layer in base_model.layers:
    layer.trainable = False  # freeze base model

model.compile(optimizer=Adam(learning_rate=0.0001), loss="binary_crossentropy", metrics=["accuracy"])

print("🧠 Training model...")
history = model.fit(
    datagen.flow(X_train, y_train, batch_size=BATCH_SIZE),
    validation_data=(X_val, y_val),
    epochs=EPOCHS,
    verbose=1
)

# =============================
# Save model
# =============================
model.save("deepfake_detector.h5")
print("✅ Model saved as deepfake_detector.h5")

# =============================
# Plot training history
# =============================
plt.figure(figsize=(10,4))
plt.subplot(1,2,1)
plt.plot(history.history["accuracy"], label="Train Acc")
plt.plot(history.history["val_accuracy"], label="Val Acc")
plt.legend()
plt.title("Accuracy")

plt.subplot(1,2,2)
plt.plot(history.history["loss"], label="Train Loss")
plt.plot(history.history["val_loss"], label="Val Loss")
plt.legend()
plt.title("Loss")

plt.savefig("training_history.png")
print("📊 Training history saved as training_history.png")
