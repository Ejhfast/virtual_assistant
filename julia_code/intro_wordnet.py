from nltk.corpus import wordnet as wn 
from nltk.corpus import wordnet_ic
from itertools import product
import sys
from spacy.en import English
from numpy import dot
from numpy.linalg import norm
import operator


#Generates new commands by replacing a certain word with its synonyms
#Asks user for which word to replace
def gen_syn_commands_for_word(command):
	word_to_change = raw_input("Which word do you want to change? ")
	gen_commands = gen_syn_commands(command,word_to_change)

#Generates new commands by replacing every combination of words with its synonyms (not computationally feasible, may be better restricted)
def gen_syn_commands_for_all(command):
	gen_commands = []
	all_syns = []
	for word in command:
		new_syns = get_synonyms(word)
		new_syns.append(word)
		print(new_syns)
		all_syns.append(list(set(new_syns)))
	gen_commands = set(list(product(*all_syns)))
	for c in gen_commands:
		print " ".join(c)

#Generates new commands by replacing one word
def gen_syn_commands(command,word_to_change):
	synonyms = get_synonyms(word_to_change)
	ix_to_change = -1
	gen_commands = []
	for i,word in enumerate(command):
		if word.lower() == word_to_change.lower():
			ix_to_change = i 
	if ix_to_change == -1:
		print("That word is not in the command.")
		return []
	for syn in synonyms:
		comm_copy = command
		comm_copy[ix_to_change] = syn
		comm_copy_str = " ".join(comm_copy)
		gen_commands.append(comm_copy_str)
	return set(gen_commands)

#Get synonyms from a word's synsets
def get_synonyms(word):
	syns = []
	for syn in wn.synsets(word):
		for l in syn.lemmas():
			syns.append(l.name())
	return syns

#Get cosine between vectors
def cosine(v1,v2):
	if norm(v1) == 0 or norm(v2) == 0:
		return 0
	return (dot(v1,v2) / (norm(v1) * norm(v2)))

#Calculate wordnet similarity between synonyms of a word (should be 1)
def calc_sim_between_syns(word):
	syns = set(get_synonyms(word))
	print syns
	for s in syns:
		if s != word:
			calc_sim_between_words(word,s)

#Calculate word2vec similarity between synonyms of a word
def calc_w2v_sim_between_syns(word):
	syns = set(get_synonyms(word))
	for syn in syns:
		calc_sim_between_words(word,syn)

#Calculates similarity between two words in several ways:
#1. Wu-Palmer Similarity max between synonyms of each word
#2. Path similarity max between synonyms of each word
#3. W2V cosine similarity between words
def calc_sim_between_words(w1,w2):
	nlp = English()
	w1_vec = nlp.vocab[unicode(w1,'utf-8')].repvec
	#w2_vec = nlp.vocab[unicode(w2,'utf-8')].repvec
	#w1_vec = nlp.vocab[w1].repvec
	w2_vec = nlp.vocab[w2].repvec
	synsets1 = wn.synsets(w1)
	synsets2 = wn.synsets(w2)
	syns1 = get_synonyms(w1)
	syns2 = get_synonyms(w2)

	w2v_synsets1 = [nlp.vocab[w].repvec for w in syns1 if w in nlp.vocab]
	w2v_synsets2 = [nlp.vocab[w].repvec for w in syns2 if w in nlp.vocab]

	best_wup = max(s1.wup_similarity(s2) for s1, s2 in product(synsets1, synsets2))
	best_path = max(s1.path_similarity(s2) for s1, s2 in product(synsets1, synsets2))
	cos_sim = cosine(w1_vec,w2_vec)
	
	print("Best Wu-Palmer Similarity between {} and {}: {}".format(w1,w2,best_wup))
	print("Best Path Similarity between {} and {}: {}".format(w1,w2,best_path))
	print("Word2Vec Similarity between {} and {}: {}".format(w1,w2,cos_sim))

def main():
	command = raw_input("What is your command? ").split()
	syn_commands = gen_syn_commands_for_all(command)
	#calc_sim_between_words(sys.argv[1],sys.argv[2])
	#calc_w2v_sim_between_syns(sys.argv[1])


if __name__ == "__main__":
	main()
