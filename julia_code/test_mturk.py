from __future__ import print_function
from nltk.corpus import wordnet as wn 
from itertools import product
from numpy import dot
from numpy.linalg import norm
import sys
from collections import OrderedDict
import operator
import csv
import re
import random
from spacy.en import English

#Results from the first MTurk task
#Given 80 variants of 3 commands, how well could new variants be matched?
#24 variants used as "test" set, were matched to the remaining variants in the "training set"

#Cosine similarity
def cosine(v1,v2):
	if norm(v1) == 0 or norm(v2) == 0:
		return 0
	return (dot(v1,v2) / (norm(v1) * norm(v2)))

#Calculate similarity between words
def calc_sim_between_words(w1,w2):
	w1_vec = nlp.vocab[w2].repvec
	w2_vec = nlp.vocab[w2].repvec
	cos_sim = cosine(w1_vec,w2_vec)
	return cos_sim

#Formats csv file, puts each command in list
def format_csv_file(filename):
	
	ex1 = "Send [abc.txt] as a [PDF] to [Joe] via [email]"
	ex2 = "Turn [Flux] [on] when I finish using [Microsoft Word]"
	ex3 = "Close [Mendeley] if it hasn't been used in [a week]"

	pdf_joe = [ex1]
	toggle_flux = [ex2]
	close_app = [ex3]

	with open(filename) as csvfile:
		reader = csv.DictReader(csvfile)
		for i,row in enumerate(reader):
			if i <= 9:
				pdf_joe = pdf_joe + row.values()
			elif i <= 19:
				toggle_flux = toggle_flux + row.values()
			else:
				close_app = close_app + row.values()

	pdf_joe_sample = [pdf_joe.pop(random.randrange(len(pdf_joe))) for _ in xrange(8)]
	toggle_flux_sample = [toggle_flux.pop(random.randrange(len(toggle_flux))) for _ in xrange(8)]
	close_app_sample = [close_app.pop(random.randrange(len(close_app))) for _ in xrange(8)]
	return(pdf_joe,toggle_flux,close_app,pdf_joe_sample,toggle_flux_sample,close_app_sample)

#result files 1-8 contain training examples
def make_result_csv(res1,res2,res3):
	with open('results8.csv','w') as csvfile:
		writer = csv.writer(csvfile)
		writer.writerow(res1)
		writer.writerow(res2)
		writer.writerow(res3)

#sample files 1-8 contain testing examples
def make_sample_csv(sample1,sample2,sample3):
	with open('samples8.csv','w') as csvfile:
		writer = csv.writer(csvfile)
		writer.writerow(sample1)
		writer.writerow(sample2)
		writer.writerow(sample3)

#really don't know why I did it this way, but retrieves results and puts them in 3 lists
def retrieve_results(filename):
	row1 = []
	row2 = []
	row3 = []
	with open(filename,'r') as csvfile:
		reader = csv.reader(csvfile)
		for i, row in enumerate(reader):
			if i == 0:
				row1 = row
			elif i == 1:
				row2 = row
			elif i == 2:
				row3 = row
	return(row1,row2,row3)

#First pass at matching: literal string matching with no processing
def compare_samples_to_results(samples,results,command_num):
	correct = 0 
	total = len(samples)
	for s in samples:
		if s in results:
			correct += 1
	accuracy = float(correct)/total
	print("Command {} had {} matches out of {} examples, with an accuracy of {}".format(command_num,correct,total,accuracy))


#Normalization pass 1 
#Remove punctuation at end of sentence (done)
#Remove brackets (done)
#Remove non-bracket, non-alphabetic characters at beginning of sentence (done)
#Lowercase first letter 
#lowercase all letters? <-- did this one for now, might change

def normalize_responses_1(responses):
	new_responses = []
	pat1 = re.compile(r"\s*\.\s*$")
	pat2 = re.compile(r"[\[\]]")
	pat3 = re.compile(r"^[^A-Za-z]+")

	for resp in responses:
		resp = re.sub(pat1,r"",resp)
		resp = resp.replace("["," ")
		resp = resp.replace("]"," ")
		resp = " ".join(resp.split())
		resp = re.sub(pat3,r"",resp)
		resp = resp.lower()
		new_responses.append(resp)
	return new_responses

#Never finished, but normalization for doing something with wn 
def normalize_responses_wn(responses):
	new_responses = []
	pat1 = re.compile(r"\s*\.\s*$")
	pat2 = re.compile(r"[\[\]]")
	pat3 = re.compile(r"^[^A-Za-z]+")

	for resp in responses:
		resp = re.sub(pat1,r"",resp)
		resp = resp.replace("["," ")
		resp = resp.replace("]"," ")
		resp = " ".join(resp.split())
		resp = re.sub(pat3,r"",resp)
		resp = resp.lower()
		resp = resp.decode("utf-8")
		new_responses.append(resp)
	return new_responses

#another round of normalizing, standardizing
#This is still before any NLP stuff 
#The next round will be related words (wordnet and word_embeddings)
#The round after will incorporate POS, parsing, etc info
#Following round will investigate what can be cut from the sentence

#remove commas
#allow for subset matches (one variant is fully contained in another or vice versa)
#Preserve order or no? Probably should (I miss you vs you miss me), consider with POS info 
#BOW model -> turn test and training into list, see if one is a subset of another
#Print to make sure that they are correct
def normalize_responses_2(responses):
	first_pass = normalize_responses_1(responses)
	new_responses = []

	for resp in first_pass:
		resp = resp.replace(",","")
		resp = " ".join(resp.split())
		new_responses.append(resp)
	return new_responses

#Normalizes both the training and testing and compares the normalized lists
def compare_samples_to_results_after_n1(samples,results,command_num):
	new_samples = normalize_responses_1(samples)
	new_results = normalize_responses_1(results)
	compare_samples_to_results(new_samples,new_results,command_num)

#See if one sentence is a subset of another, NOT considering word order(treated as BOW)
def is_subset_no_order(a,b):
	for word in a:
		if word not in b:
			return False
	return True


#Evaluation of normalization2 (n2, BOW) on data
#Worked artificially well because a lot of individual Turkers used the same words and changed order
#Doesn't preserve meaning enough
def compare_samples_to_results_after_n2(samples,results,command_num):
	new_samples = normalize_responses_2(samples)
	new_results = normalize_responses_2(results)
	correct = 0 
	total = len(new_samples)
	for s in new_samples:
		if s in new_results:
			correct += 1
		else:
			for r in new_results:
				if is_subset_no_order(s.split(),r.split()) or is_subset_no_order(r.split(),s.split()):
					correct += 1
					#print("{}   {}\n".format(s,r),file=log)
					break

	accuracy = float(correct)/total
	print("Command {} had {} matches out of {} examples, with an accuracy of {}".format(command_num,correct,total,accuracy))


#Not computationaly feasible, so not yet done, but idea is to expand the training set by replacing all words by all synonyms
#with the same POS
def expand_results_pos_syns(results):
	new_results = []
	for command in results:
		r_syn1 = gen_syn_commands_for_pos(command)
		new_results = new_results + r_syn1
	return new_results

#Would compare results after using synset expansion, but doesn't work for aforementioned reasons
def compare_samples_to_results_after_wn_expansion(samples,results,command_num):
	responses = normalize_responses_wn(results)
	exp_results = expand_results_pos_syns(responses)
	print("Responses len: {}".format(len(responses)))
	print("Expanded len: {}".format(len(exp_results)))
	compare_samples_to_results(samples,exp_results,command_num)



def main():
	filename = "mturk_results_prototype.csv"
	res1,res2,res3,sample1,sample2,sample3 = format_csv_file(filename)
	make_result_csv(res1,res2,res3)
	#make_sample_csv(sample1,sample2,sample3)

	# for i in xrange(1,9):
	# 	print("Sample {}".format(i))
	# 	res_file = "results" + str(i) + ".csv"
	# 	sam_file = "samples" + str(i) + ".csv"
	# 	r1,r2,r3 = retrieve_results(res_file)
	# 	s1,s2,s3 = retrieve_results(sam_file)
	# 	if i == 1:
	# 		commands = normalize_responses_2(r1)
	# 		pos_tags = get_pos_tags(commands[0])
	# 		for i,word in enumerate(commands[0].split()):
	# 			pos = pos_tags[i]
	# 			syns_pos = get_synonyms_pos(word,pos)
	# 			print(len(syns_pos))
	# 			for syn in syns_pos:
	# 				print(calc_sim_between_words(word,syn))
	# 			syns_pos_w2v = get_synonyms_pos_w2v(word,pos)
	# 			for syn in syns_pos_w2v:
	# 				print(calc_sim_between_words(word,syn))
	# 			print(syns_pos_w2v)

			#compare_samples_to_results_after_wn_expansion(s1,r1,1)
			 
		#compare_samples_to_results_after_wn_expansion(s2,r2,2)
		#compare_samples_to_results_after_wn_expansion(s3,r3,3)
		





if __name__ == "__main__":
	main()

