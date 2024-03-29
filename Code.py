!pip install gradio
!pip install --upgrade typing-extensions
!pip install --upgrade gradio

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
import tensorflow as tf
from sklearn.metrics import confusion_matrix, classification_report
import requests
from io import StringIO

url = 'https://drive.google.com/uc?id=1z9jm3-05QHZYGAUik6Ry2OsxWYc2rPHF'
response = requests.get(url) # retrieving dataset from a given URL

data = pd.read_csv(StringIO(response.text)) #load dataset to notebook as dataframe

"""# EDA"""

data.head()

data.describe()

data['label'].hist(figsize = (10,10))
plt.show()

label_mapping = {'NEGATIVE': 0, 'NEUTRAL': 1, 'POSITIVE': 2}
data['label'] = data['label'].map(label_mapping)

from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
data.iloc[:, :-1] = scaler.fit_transform(data.iloc[:, :-1])

data.head()

X = data.drop('label', axis=1)
y = data['label']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

X_test, X_val, y_test, y_val = train_test_split(X_test, y_test, test_size=0.2, random_state=42)

model = tf.keras.Sequential([
    tf.keras.layers.Input(shape=(X_train.shape[1],)),
    tf.keras.layers.Dense(256, activation='relu'),
    tf.keras.layers.Dropout(0.5),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dropout(0.5),
    tf.keras.layers.Dense(3, activation='softmax')
])

tf.keras.utils.plot_model(model, show_layer_names=False, rankdir='LR')



model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

history = model.fit(X_train, y_train, validation_split=0.2, epochs=70, batch_size=32, verbose=2)

plt.figure(figsize=(12, 6))
plt.subplot(1, 2, 1)
plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title('Model Accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend(['Train', 'Validation'], loc='upper left')

plt.subplot(1, 2, 2)
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Model Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend(['Train', 'Validation'], loc='upper left')

plt.tight_layout()
plt.show()

model_acc = model.evaluate(X_test, y_test, verbose=0)[1]
print("Test Accuracy: {:.3f}%".format(model_acc * 100))

y_pred = np.argmax(model.predict(X_test), axis=-1)

cm = confusion_matrix(y_test, y_pred)
# Visualization of Confusion Matrix
plt.figure(figsize=(8, 8))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", cbar=False, xticklabels=label_mapping.keys(), yticklabels=label_mapping.keys())
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.title('Confusion Matrix')
plt.show()

clr = classification_report(y_test, y_pred, target_names=label_mapping.keys())
print(clr)

import gradio as gr
def predict(file):
    try:
        ++
        df = pd.read_csv(file.name)

        preds = model.predict(df.iloc[0].values.reshape(1, -1)).flatten()
        emotion_labels = {0: 'NEGATIVE', 1: 'NEUTRAL', 2: 'POSITIVE'}
        preds = {emotion_labels[i]: float (preds[i])for i in range(3)}

        df = pd.read_csv(file.name)
        sample = df.loc[0, 'fft_0_b':'fft_749_b']
        plt.figure(figsize=(16, 10))
        plt.plot(range(len(sample)), sample)
        plt.title("EEG Time-Series Data")
        plt.xlabel("Time")
        plt.ylabel("Amplitude")
        return plt, preds
    except Exception as e:
        return f"Error: {str(e)}"

iface = gr.Interface(
    title = 'EEG Classification for Deep Learning Algorithm',
    description = "Model and design by Muhammad Rafli and Hafizh Saputra",
    fn= predict,
    inputs=gr.File(label="Upload CSV File", type='filepath'),
    outputs=[gr.Plot(label="EEG Plot"), gr.Label(num_top_classes = 3, label="Predicted Emotion")],
    allow_flagging = "never"
    )

# Launch the Gradio interface
iface.launch()
