import pandas as pd
import matplotlib.pyplot as plt

from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

bank_data = pd.read_csv('bank.csv', sep = ';')
bank_features = bank_data.drop('y', axis = 1)
bank_output = bank_data.y
bank_features = pd.get_dummies(bank_features)
bank_output = bank_output.replace({
        'no': 0,
        'yes': 1})
X_train, X_test, y_train, y_test = train_test_split(bank_features, bank_output, test_size=0.25,random_state=42)
bank_model = LogisticRegression(C = 1e6, solver='liblinear')
bank_model.fit(X_train, y_train)
accuracy_score = bank_model.score(X_train, y_train)
print(accuracy_score)
plt.bar([0, 1], [len(bank_output[bank_output == 0]), len(bank_output[bank_output == 1])])
plt.xticks([0, 1])
plt.xlabel('Class')
plt.ylabel('Count')
plt.show()
print('Positive cases: {:.3f}% of all'.format(bank_output.sum() / len(bank_output) * 100))
predictions = bank_model.predict(X_test)
from sklearn.metrics import classification_report
print(classification_report(y_test,predictions))