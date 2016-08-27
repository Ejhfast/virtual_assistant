from __future__ import print_function
from spacy.en import English
from numpy import dot
from numpy.linalg import norm
import sys
from collections import OrderedDict
import operator
import csv
import re

nlp = English()


#returns file contents as spacy doc
def get_doc(f):
	if len(sys.argv) <= 1:
		with open(f,'r') as f:
			d = f.read()
	else:
		d = sys.argv[1]
	d2 = unicode(d,"utf-8")
	doc = nlp(d2)
	return doc

#return doc as list of sentences
def get_sentences(doc):
	return list(doc.sents)

#return doc as list of lines
def get_lines(f):
	with open(f,'r') as f:
		d = f.readlines()
		lines = [nlp(unicode(line,"utf-8")) for line in d]
	return lines

#gets dependency parse of sentences and get POS and named entities (if any) from tokens 
#writes into file
def get_pos_and_ents(sentences,f):
	log = open(f, "w")
	for i in range(len(sentences)):
		print("SENTENCE:",file = log)
		print(sentences[i],file = log)
		doc_sent = nlp(unicode(str(sentences[i]),"utf-8"))
		print("\n",file = log)
		print("TOKENS AND POS:",file=log)
		for token in sentences[i]:
			print(token, token.pos_,file = log)
			#if token.pos_ == "NUM":
				#print "NUMBER: {}".format(token)
		print("\n",file = log)
		print("NAMED ENTITIES:",file=log)
		for ent in doc_sent.ents:
			print(ent, ent.label_,file = log)	
		print("\n",file=log)
		print("DEPENDENCIES:",file=log)
		for token in sentences[i]:
			print(token.orth_.encode("utf-8"), token.dep_.encode("utf-8"), token.head.orth_.encode("utf-8"),
			 [t.orth_.encode("utf-8") for t in token.lefts], [t.orth_.encode("utf-8")for t in token.rights],file=log)





#Gets word vector of a combination of other words (accounds for addition and subtraction)
#Parameter args looks like: king - man + woman
def word_embedding(args):
	first_word = unicode(args[0],"utf-8")
	op = "+"
	result = nlp.vocab[first_word].repvec
	for word in args[1:]:
		if word == "-":
			op = "-"
		elif word  == "+":
			op = "+"  
		else:
			word_vec = nlp.vocab[unicode(word,"utf-8")].repvec
			if op == "+":
				result = result + word_vec
			else:
				result = result - word_vec
	return result

#Find words with the highest cosine similarities to the vec parameter 
def similar_words(vec):
	allWords = list({w for w in nlp.vocab if w.has_vector and w.orth_.islower() and w.lower_ != sys.argv[1]})
	cosine = lambda v1, v2: dot(v1,v2) / (norm(v1) * norm(v2))
	allWords.sort(key=lambda w: cosine(w.repvec, vec))
	allWords.reverse()
	#top_words = list(word.orth_.encode('utf-8') for word in allWords[:10])
	top_words = allWords[:10]
	#for word in top_words:
	 	#print(word.decode('utf-8'),)
	return top_words

#Given a word's vec representation and POS, find most similar words with the same POS as the original
def similar_words_with_pos(vec,pos):
	allWords = list({w for w in nlp.vocab if w.has_vector and w.orth_.islower() and w.lower_ != sys.argv[1] and nlp(w.orth_)[0].pos_ == pos})
	cosine = lambda v1, v2: dot(v1,v2) / (norm(v1) * norm(v2))
	allWords.sort(key=lambda w: cosine(w.repvec, vec))
	allWords.reverse()
	#top_words = list(word for word in allWords[:10])
	top_words = allWords[:10]
	#for word in top_words:
	 	#print(word.orth_,nlp(word.orth_)[0].pos_)
	return top_words


#Compare results from any word, and confined by POS
def sim_words_to_index(vec,pos):
	top_words = similar_words(vec)
	top_words_pos = similar_words_with_pos(vec,pos)
	cosine = lambda v1, v2: dot(v1,v2) / (norm(v1) * norm(v2))

	print("-----MOST SIMILAR WORDS------")
	for w in top_words:
		tw = nlp(w.orth_)[0]
		co = cosine(w.repvec,vec)
		co_str = "{0:.4f}".format(co)

		print(w.orth_,co_str,tw.pos_)
	print("------NOW WITH POS-------") 
	for w in top_words_pos:
		tw = nlp(w.orth_)[0]
		co = cosine(w.repvec,vec)
		co_str = "{0:.4f}".format(co)
		print(w.orth_,co_str,tw.pos_)

#Bad attempts to do argument matching
def map_all_commands(f,fields,mapping):
	with open('arguments.csv','w') as csvfile:
		writer = csv.DictWriter(csvfile, fieldnames = fields)
		writer.writeheader()
		#sentences = get_sentences(doc)
		sentences = get_lines(f)
		for sentence in sentences:
			args = mapping(sentence)
			row = {fields[0]:args[0], fields[1]: args[1],fields[2]: args[2],fields[3]: args[3],fields[4]:args[4],fields[5]:args[5]}
			writer.writerow(row)

#Really bad way to map args for the messaging friend command
def map_args_message_friend(command):
	tokens = nlp(unicode(str(command),"utf-8"))
	action = ""
	toggle = ""
	current_app = ""
	other_app = ""
	for token in tokens:
		print(token,token.pos_,token.dep_,token.head.orth_,token.head.dep_)
	for i in range(len(tokens) - 1):
		t1 = tokens[i]
		t2 = tokens[i+1]
		if t1.dep_ == u'ROOT':
			action = t1.orth_
		elif t1.dep_ == 'dobj' and t1.pos_ != "PROPN" and t1.head.dep_ == "ROOT":
			subtree_span = tokens[t1.left_edge.i : t1.right_edge.i + 1]
			if subtree_span[0].dep_ == "mark" or subtree_span[0].orth_ == "that":
				subtree_span = subtree_span[1:]
			message = subtree_span.text.encode('utf-8')
		elif (t1.dep_ == u'dobj' and t1.head.dep_ == "ROOT" and t1.pos_ == "PROPN") or t1.dep_ == "dative":
			recipient = t1.orth_
		elif (t1.dep_ == u'pobj' and t1.head.dep_ == "prep" and t1.pos_ == "PROPN" and ((t1.head).head).dep_ == "ROOT"):
			recipient = t1.orth_
		elif t1.pos_ == u'NUM' and t2.pos_ == u'NOUN' and ((t2.head).head).dep_ == "ROOT":
			time = t1.orth_ + " " + t2.orth_
		elif t1.dep_ in ('xcomp','ccomp') or (t1.dep_ == "nsubj" and (t1.head.dep_ == "prep" or t1.head.dep_ == "det")):
			subtree_span = tokens[t1.left_edge.i : t1.right_edge.i + 1]
			if subtree_span[0].dep_ == "mark":
				subtree_span = subtree_span[1:]
			message = (subtree_span.text).encode('utf-8')
	
	return tokens,action,recipient,time,message

#Really bad way to match args to toggle apps
def map_args_toggle_apps(command):
	tokens = nlp(unicode(str(command),"utf-8"))
	action = ""
	toggle = ""
	current_app = ""
	other_app = ""
	print(tokens)
	for token in tokens:
		print(token,token.pos_,token.dep_,token.head.orth_,token.head.dep_)
	for i in range(len(tokens)):
		t1 = tokens[i]
		if t1.dep_ == u'ROOT':
			action = t1.orth_
		elif t1.orth_.lower() == "on" or t1.orth_.lower() == "off":
			toggle = t1.orth_
		elif (t1.pos_ == "NOUN" or t1.pos_ == "PROPN") and t1.head.dep_ == "ROOT":
			other_app = t1.orth_
		elif t1.pos_ == "NOUN" or t1.pos_ == "PROPN" or (t1.dep_ == "dobj" and (sum(1 for _ in t1.children) == 0)):
			current_app = t1.orth_
			if t1.left_edge.dep_ == "det":
				current_app = t1.left_edge.orth_ + " " + t1.orth_
	return tokens,action,toggle,current_app,other_app
		
# for token in sentences[i]:
# 	print(token.orth_.encode("utf-8"), token.dep_.encode("utf-8"), token.head.orth_.encode("utf-8"),
# 	 [t.orth_.encode("utf-8") for t in token.lefts], [t.orth_.encode("utf-8")for t in token.rights],file=log)

#Really bad way to match args for shush
def map_args_shush(command):
	tokens = nlp(unicode(str(command),"utf-8"))
	action = ""
	app = "everything"
	blank = ""
	verbs = [x for x in tokens if x.pos_ == "VERB"]

	if len(verbs) == 0:
		action = tokens[0]
		for i in range(len(tokens)):
			t = tokens[i]
			if t.pos_ == "NOUN" or t.pos_ == "PROPN":
				app = t.orth_
				if tokens[i-1].pos_ == "DET":
					app = tokens[i-1].orth_ + " " + t.orth_
			elif t.dep_ == "dobj":
				app = (tokens[t.left_edge.i : t.right_edge.i + 1]).text.encode("utf-8")
				break
	else:
		for t in tokens:
			if t.pos_ == "VERB":
				subtree_span = tokens[t.left_edge.i : t.right_edge.i + 1]
				if subtree_span[0].dep_ == "aux":
					subtree_span = subtree_span[1:]
				action = (subtree_span.text).encode('utf-8')
	return tokens,action,app,blank,blank

#Detect file structure regex 
def has_file_structure(t):
	m = re.search(r"(\w+)\.(\w{2,5})",t)
	if m == None:
		return False
	return True

#Really bad way to send a file
def map_args_send_file(command):
	tokens = nlp(unicode(str(command),"utf-8"))

	action = ""
	filename = "this"
	filetype = ""
	contact = ""
	verbs = [x for x in tokens if x.pos_ == "VERB"]

	for i in range(len(tokens)):
		token = tokens[i]
		print(token,token.pos_,token.dep_,token.ent_type_,token.head.orth_,token.head.dep_)

		if token.pos_ == "VERB":
			action = token.orth_	

		elif has_file_structure(str(token)):
			filename = token.orth_

		elif token.ent_type_ == "PERSON" or ((token.pos_ == "PROPN" or token.pos_ == "NOUN") and (token.dep_ == "dative" or token.head.dep_ == "dative")):
			contact = (tokens[token.left_edge.i : token.right_edge.i + 1].text).encode('utf-8')

		elif (token.pos_ == "NOUN" or token.pos_ == "PROPN") and token.dep_ == "pobj":
			filetype = token.orth_
		elif (token.pos_ == "NOUN" or token.pos_ == "PROPN") and token.left_edge.dep_ == "det":
			filetype = token.orth_
		elif (token.pos_ == "NOUN" or token.pos_ == "PROPN") and sum(1 for _ in token.children) > 0:
			filetype = token.orth_
			if token.left_edge.dep_ == "compound":
				filetype = token.left_edge.orth_ + " " + token.orth_
		elif token.pos_ == "NOUN" and (sum(1 for _ in token.children) == 0):
			contact = token.orth_
		
	return tokens,action,filename,filetype,contact,''

def test():
	for w in nlp.vocab:
		print(w, nlp(unicode(w.orth_,'utf-8'))[0].pos_)


#Calculate cosine between two vectors
def cosine(v1,v2):
	return (dot(v1,v2) / (norm(v1) * norm(v2)))

#Given a doc and a list of arg params, build dict of dicts containing 
#similarity scores between each token and each arg param
def build_token_sim_dict(doc,my_list):
	token_dict = {}
	token_list = [nlp(unicode(w,'utf-8'))[0] for w in my_list]
	for p in token_list:
		if p not in token_dict:
			token_dict[str(p)] = {}
		for t in doc:
			if t not in token_dict[str(p)]:
				score = cosine(p.repvec,t.repvec)
				token_dict[str(p)][str(t)] = score
	return token_dict


#Given the similarity dict, match the highest arg param and token, then
#remove them, then match the next highest pair, and continue 
#Returns list of these pairs and the score
def most_sim_tokens(token_dict):
	copy_dict = token_dict
	sim_pairs = []
	num_params = len(token_dict)
	while num_params > 0 and len(copy_dict[copy_dict.keys()[0]]) > 0:
		candidates = []
		for p in copy_dict:
			hi_score = max(copy_dict[p].values())
			cand_t = max(copy_dict[p].iteritems(), key=operator.itemgetter(1))[0]
			candidates.append((p,cand_t,hi_score))
		max_score = max(candidates, key=operator.itemgetter(2))[2]
		p_max = max(candidates, key=operator.itemgetter(2))[0]
		t_max = max(candidates, key=operator.itemgetter(2))[1]
		for p in copy_dict:
			del copy_dict[p][t_max]
		del copy_dict[p_max]
		num_params = num_params - 1
		sim_pairs.append([p_max,t_max,max_score])
	return sim_pairs

#Builds the similarity dict, matches args and tokens by similarity, and prints
def compare_to_params(doc,params):
	sim_dict = build_token_sim_dict(doc,params)
	sim_pairs = most_sim_tokens(sim_dict)
	for x in sim_pairs:
		print(x)

def main():
	#f = 'examples5.txt'
	#doc = get_doc(f)
	#fields = ['sentence','action','filename','filetype','contact','']
	#mapping = map_args_send_file
	#map_all_commands(f,fields,mapping)
	#sentence = "Tell Joe in 5 min that I'm here."
	#get_pos_and_ents(sentences,filename)
	#get_pos_and_ents(sentences)
	# while True:
	# 	command = raw_input("Enter command here: ")
	# 	if command == "quit":
	# 		return
	# 	else:
	# 		map_args(command)
	#token_dict = build_token_sim_dict(doc)
	#most_sim_pair = most_sim_tokens(token_dict)
	#print most_sim_pair

	#assume that input is the command followed by the index of the word to look up
	doc = nlp(unicode(" ".join(sys.argv[1:-1]),"utf-8"))
	index = int(sys.argv[-1])
	token = doc[index]
	pos = token.pos_
	print("POS: {}".format(token.pos_),token)
	vec = token.repvec
	#sim_words_to_index(vec,pos)
	# params = ["contact","app","file","person","notify", "switch"]
	params = ["toggle","app","application"]

	compare_to_params(doc,params)

	# w = nlp(unicode("quiet","utf-8"))[0]
	# print(token.similarity(w) * 2)
	# x = nlp(unicode("lanky","utf-8"))[0]
	# print(token.similarity(x) * 2)
	#vec = word_embedding(sys.argv[1:-1])
	#similar_words(vec)
	#print("--------NOW WITH SAME POS---------")
	#similar_words_with_pos(vec)
	#test()
	

if __name__ == "__main__":
	main()