import sqlite3
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import matplotlib.pyplot as plt
from sklearn.model_selection import learning_curve
import pickle
import re

KULULAJIT = {
    1: "Ammattikirjallisuus",
    2: "Edustuskulut",
    3: "Henkilökunnan koulutus",
    0: "ATK-laite ja -ohjelmakulut",
    4: "Matkakulut",
    7: "Polttoainekulut",
    5: "Posti- ja lähetyskulut",
    6: "Toimistotarvikkeet"
}

DATABASE_PATH = "kululajit.db"

QUERY = """
SELECT seliteteksti, kululaji
FROM seliteteksti;  -- Replace with your table name
"""

def preprocess(text):
    text = text.lower()
    text.replace('ä', 'ae').replace('ö', 'oe')
    text = re.sub(r'[^a-zäöå\s]', '', text)
    return text


conn = sqlite3.connect(DATABASE_PATH)
data = pd.read_sql_query(QUERY, conn)

conn.close()

# Encode the target variable
data['kululaji_encoded'] = data['kululaji'].astype('category').cat.codes

# Split the data
X_train, X_test, y_train, y_test = train_test_split(
    data['seliteteksti'], data['kululaji_encoded'], test_size=0.2, random_state=42
)

# Text vectorization using TF-IDF
vectorizer = TfidfVectorizer() #CountVectorizer()
X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

"""pca = PCA(n_components=3)
X_train_3d = pca.fit_transform(X_train_tfidf.toarray())

# Visualize the data points in 3D
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

# Create scatterplot with labels
unique_classes = np.unique(y_train)
colors = plt.cm.viridis(np.linspace(0, 1, len(unique_classes)))

for color, cls in zip(colors, unique_classes):
    indices = y_train == cls  # Select points belonging to the current class
    ax.scatter(
        X_train_3d[indices, 0],
        X_train_3d[indices, 1],
        X_train_3d[indices, 2],
        label=f"{KULULAJIT[cls]} (Encoded: {cls})",
        edgecolor='k',
        s=50
    )

# Add legend
ax.legend(title="Kululaji", loc="upper left", fontsize=9)

# Add titles and labels
ax.set_title("TF-IDF Features Visualized with 3D PCA", fontsize=14)
ax.set_xlabel("Principal Component 1")
ax.set_ylabel("Principal Component 2")
ax.set_zlabel("Principal Component 3")
plt.show()"""


# Train the logistic regression model
model = LogisticRegression()
model.fit(X_train_tfidf, y_train)

# Make predictions
y_pred = model.predict(X_test_tfidf)

kululaji_counts = data['kululaji'].value_counts()

# Print the counts
print(kululaji_counts)

kululaji_mapping = data[['kululaji', 'kululaji_encoded']].drop_duplicates()

# Print the mapping of 'kululaji' to its encoded code
print(kululaji_mapping)

new_inputs = [
            "Junalippu työmatkalle Helsinkiin",
            "Lentolippu työmatkalle Helsinkiin",
            "verkko ja pilvipalveluiden ylläpitokulut",
            "Käyttöoikeus ohjelmiston lisenssiin asiakkaille",
            "seminaarimaksut kansainväliseen konferenssiin",
            "Lounas asikkaan kassa",
            "Yöpyminen hotellissa",
            ]

for new_input in new_inputs:
    new_input_tfidf1 = vectorizer.transform([preprocess(new_input)])
    new_pred1 = model.predict(new_input_tfidf1)
    print(f"Input: {new_input} Predicted class: {new_pred1[0]}")

with open('model.pkl', 'wb') as model_file:
    pickle.dump(model, model_file)
with open('vectorizer.pkl', 'wb') as vectorizer_file:
    pickle.dump(vectorizer, vectorizer_file)

train_sizes, train_scores, test_scores = learning_curve(model, X_train_tfidf, y_train, cv=5)
plt.plot(train_sizes, train_scores.mean(axis=1), label="Train score")
plt.plot(train_sizes, test_scores.mean(axis=1), label="Test score")
plt.xlabel('Training Size')
plt.ylabel('Score')
plt.legend()
plt.show()

print(test_scores.max())
print(test_scores)


