import sys
import csv
import re
import numpy as np 
from sklearn.feature_extraction.text import CountVectorizer
from sklearn import metrics
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.svm import LinearSVC
from sklearn.linear_model import LogisticRegression


def remove_args(docs):
	new_docs = []
	for command in docs:
		new_command = re.sub(r'\[.*?\]',r'ARG',command)
		new_docs.append(new_command)
	return new_docs

def remove_brackets(docs):
	new_docs = []
	for command in docs:
		new_command = command.replace("[",' ')
		new_command = new_command.replace("]",' ')
		new_command = " ".join(new_command.split())
		new_command = new_command.replace(" .",".")
		new_docs.append(new_command)
	return new_docs


f = 'mturk_sklearn_shuffled5.csv'
snum = "Sample 5"
dataset = list(csv.reader(open(f)))
documents = [row[1] for row in dataset]
labels = [row[0] for row in dataset]
train_docs = documents[:861]
test_docs = documents[861:]
#train_docs = remove_args(train_docs)
#test_docs = remove_brackets(test_docs)

vec = CountVectorizer(ngram_range=(1, 2)) #unigram and bigram features
X_train = vec.fit_transform(train_docs).toarray()
X_test = vec.transform(test_docs).toarray() #uses training features
y_train = np.array(labels[:861])
y_test = np.array(labels[861:])


#model = GaussianNB()
#model = SVC(class_weight='balanced')
#model = LinearSVC(class_weight='balanced')
model = LogisticRegression(class_weight='balanced') #ovr for mutliclass
model_info = "LogisticRegression"

clf = model.fit(X_train, y_train)
predicted_train = clf.predict(X_train)
predicted_test = clf.predict(X_test)

with open("classifier_results_lr_noargs2.txt","a") as log:
	log.write(model_info)
	log.write("\n")
	log.write(snum)
	log.write('\n')
	log.write("Evaluation on TRAINING DATA\n")
	log.write(metrics.classification_report(y_train, predicted_train))
	log.write("\n")
	confusion_train = (metrics.confusion_matrix(y_train, predicted_train)).astype(int)
	np.savetxt(log,confusion_train,fmt='%.3u')
	log.write("\n")
	log.write("Evaluation on TESTING DATA:\n")
	log.write(metrics.classification_report(y_test, predicted_test))
	log.write("\n")
	confusion_test = (metrics.confusion_matrix(y_test, predicted_test)).astype(int)
	np.savetxt(log,confusion_test,fmt='%.3u')
	log.write("\n")



	


