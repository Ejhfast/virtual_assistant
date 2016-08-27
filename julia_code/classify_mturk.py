import sys
import csv
import re
import numpy as np 
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer

from sklearn import metrics
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.svm import LinearSVC
from sklearn.linear_model import LogisticRegression
import numpy

#Replaces arguments (already normalized and in brackets) with ARG tokens 
#Used in training examples
def remove_args(docs):
	new_docs = []
	for command in docs:
		new_command = re.sub(r' *\[.*?\] *',r' ARG ',command)
		new_docs.append(new_command)
	return new_docs


#Removes brackets from variants
#Used in testing examples to simulate real input commands
def remove_brackets(docs):
	new_docs = []
	for command in docs:
		new_command = command.replace("[",' ')
		new_command = new_command.replace("]",' ')
		new_command = " ".join(new_command.split())
		new_command = new_command.replace(" .",".")
		new_docs.append(new_command)
	return new_docs


#Given a shuffled csv file with the first column as the labels
#and the second column as the variants, separates data into docs and labels
#then separates into training and testing with a 90%/10% split
#If include_args == True, testing examples retain the placeholder arguments, otherwise they are replaced
def get_docs_and_labels(filename,include_args):
	dataset = list(csv.reader(open(filename)))
	documents = [row[1] for row in dataset]
	labels = [row[0] for row in dataset]
	cutoff = int(len(labels) * .1)

	y_train = np.array(labels[cutoff:])
	y_test = np.array(labels[:cutoff])
	train_docs = documents[cutoff:]
	test_docs = documents[:cutoff]
	train_docs = remove_args(train_docs)

	if include_args == True:
		test_docs = remove_brackets(test_docs)
	else:
		test_docs = remove_args(test_docs)
	return train_docs,test_docs,y_train,y_test



#Given the training and testing examples, extract features 
def get_features(train_docs,test_docs,vec):
	X_train = vec.fit_transform(train_docs).toarray().astype(float)
	X_test = vec.transform(test_docs).toarray().astype(float) #uses training features
	return X_train,X_test


#Given a descriptive model_info string, runs the appropriate model
#returns predicted classes for training and testing set
def run_model(model_info,X_train,X_test,y_train):
	model = ''
	if model_info == "lr":
		model = LogisticRegression(class_weight='balanced')
	elif model_info == "svc":
		model = SVC(class_weight='balanced',C=500)
	elif model_info == "linearsvc":
		model = LinearSVC(class_weight='balanced')
	elif model_info == "nb":
		model = GaussianNB()
	else:
		return None
	clf = model.fit(X_train,y_train)
	
	predicted_train = clf.predict(X_train)
	predicted_test = clf.predict(X_test)
	return predicted_train,predicted_test,clf


#Evaluates model on training and testing data
#Returns results summaries and confusion matrices
def evaluate(predicted_train,predicted_test,y_train,y_test):
	train_results = metrics.classification_report(y_train, predicted_train)
	train_confusion = (metrics.confusion_matrix(y_train, predicted_train)).astype(int)
	test_results = metrics.classification_report(y_test, predicted_test)
	test_confusion = (metrics.confusion_matrix(y_test, predicted_test)).astype(int)
	return train_results,train_confusion,test_results,test_confusion

#Appends evaluation results and confusion matrices to file
def write_to_file(model_info,snum,eval_file,train_r,train_c,test_r,test_c):
		with open(eval_file,"a") as log:
			log.write(model_info)
			log.write("\n")
			log.write(snum)
			log.write('\n')
			log.write("Evaluation on TRAINING DATA\n")
			log.write(train_r)
			log.write("\n")
			#np.savetxt(log,train_c,fmt='%.2u')
			log.write("\n")
			log.write("Evaluation on TESTING DATA:\n")
			log.write(test_r)
			log.write("\n")
			#np.savetxt(log,test_c,fmt='%.2u')
			#log.write("\n")


#Prints results to terminal
def print_results(model_info,snum,train_r,train_c,test_r,test_c):
	print(model_info)
	print(snum)
	print("Evaluation on TRAINING DATA:")
	print(train_r)
	print(train_c)
	print("Evaluation on TESTING DATA:")
	print(test_r)
	print(test_c)

def get_important_features(vec,clf):
	feature_names = vec.get_feature_names()
	sum_coef = (clf.coef_.sum(axis=0)).tolist()
	paired_features = zip(feature_names, sum_coef)
	sorted_features = sorted(paired_features, key=lambda tup: tup[1],reverse=True)
	for x,y in enumerate(sorted_features):
		print(x,y)


def main():
	for i in range(1,6):
		include_args = True #When false, replaces test examples with ARG token. When true, just removes brackets around arguments
		filename = "sh" + str(i) + "_sklearn_70_vars_50_coms.csv"
		snum = "Sample " + str(i)
		eval_file = "nb_results_for_poster_bigram.txt"
		train_docs,test_docs,y_train,y_test = get_docs_and_labels(filename,include_args)
		vec = TfidfVectorizer(ngram_range = (1,2)) #Just doing unigram features for now, tfidf transformed

		X_train,X_test = get_features(train_docs,test_docs,vec)
		model_info = "lr"
		predicted_train,predicted_test,clf = run_model(model_info,X_train,X_test,y_train)
		train_r,train_c,test_r,test_c = evaluate(predicted_train,predicted_test,y_train,y_test)

		get_important_features(vec,clf)

		#write_to_file(model_info,snum,eval_file,train_r,train_c,test_r,test_c)
		print_results(model_info,snum,train_r,train_c,test_r,test_c)


if __name__ == "__main__":
	main()



