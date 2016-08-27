import sys
import operator
import csv
import re
import random


#Print the variants 
def print_variants(filename):
	with open(filename) as csvfile:
		reader = csv.reader(csvfile)
		for row in reader:
			for elem in row:
				print(elem)


#Replace unconventional brackets, not really relevant anymore
def replace_bad_brackets(variants):
	all_vars = []
	for command in variants:
		new_vars = []
		for var in command:
			new_var = var.replace("{",'[')
			new_var = new_var.replace("}",']')
			new_var = new_var.replace("(","[")
			new_var = new_var.replace(")","]")
			new_vars.append(new_var)
		all_vars.append(new_vars)
	return all_vars



#Remove bad data (data that doesn't have bracketed args) from data
def remove_bad_data(variants):
	all_vars = []
	for command in variants:
		new_command = []
		for elem in command:
			if "[" in elem and "]" in elem:
				new_command.append(elem)
		all_vars.append(new_command)
	return all_vars
				
#Given list of list of variants, counts number of variants for each command
def count_variants(variants):
	for i,command in enumerate(variants):
		print("Command {} has {} variants.".format(i+1,len(command)))


#Prepare files for classifier
#Makes file with the label (command # from the file with original commands)
#Variants come from cut down version of downloaded data from mturk
#Keep all command forms for each response (original and variants), get rid of other data
def smarter_make_sklearn_file(filename,newfilename):
	all_variants = list(csv.reader(open(filename)))
	orig_commands = list(csv.reader(open('commands_all_50.csv')))
	with open(newfilename,'w') as csvfile:
		writer = csv.writer(csvfile)
		for i,com in enumerate(orig_commands):
			writer.writerow([i,com[0]])
			for c in all_variants:
				if c[0] == com[0]:
					for index in range(1,len(c)):
						new_label = [i,c[index]]
						writer.writerow(new_label)


#Shuffles rows of prepared sklearn file to make training/testing splits easier
#Makes 5 shuffles, creates new file for each
def shuffle_rows(filename):
	row_list = []
	for i in range(5):
		new_file = "sh" + str(i+1) + "_sklearn_70_vars_50_coms.csv"
		with open(filename,'r') as csvfile:
			reader = csv.reader(csvfile)
			row_list = []
			for row in reader:
				row_list.append(row)
			row_list = row_list[1:]
			random.shuffle(row_list)
		
		with open(new_file,'w') as csvfile2:
			writer = csv.writer(csvfile2)
			for row in row_list[1:]:
				writer.writerow(row)

#Make shuffled files with num_examples for each class
def create_subset_shuffle(filename,num_examples,num_classes):
	with open(filename,'r') as csvfile:
		reader = csv.reader(csvfile)
		subset_list = []
		counter = [num_examples] * num_classes
		print(type(counter[0]))
		for row in reader:
			index = int(row[0]) - 1
			if counter[index] > 0:
				subset_list.append(row)
				counter[index] = counter[index] - 1
	new_name = "subset_" + str(num_examples) + ".csv"
	with open(new_name,'w') as csvfile2:
		writer = csv.writer(csvfile2)
		writer.writerows(subset_list)


#Concatenates files (I don't know why this is here)
def concat_files(file1,file2):
	vars_to_append = []
	with open(file2,'r') as csvread:
		reader = csv.reader(csvread)
		vars_to_append = list(reader)
	with open(file1,'a') as csvappend:
		writer = csv.writer(csvappend)
		writer.writerows(vars_to_append)

#Sorts commands
def sort_commands(filename):
	all_commands = []
	with open(filename,'r') as csvread:
		all_commands = list(csv.reader(csvread))
	with open(filename,'w') as csvwrite:
		sorted_commands = sorted(all_commands,key=operator.itemgetter(0))
		writer = csv.writer(csvwrite)
		writer.writerows(sorted_commands)

#Smarter way to normalize commands 
#Indexes commands corresponding to the index in the originalfile
#Extracts args from the original commands
#replaces args in variants with original args (brackets included),
#then removes extra brackets
def normalize_commands(filename):
	all_commands = list(csv.reader(open(filename)))
	orig_commands = list(csv.reader(open('commands_all_50.csv')))
	new_all_commands = []
	for command in all_commands:
		index = int(command[0])
		args_list = re.findall(r'(\[.*?\])',orig_commands[index][0])
		new_command = command[1].lower()
		for a in args_list:
			arg = a[1:-1].lower()
			if arg in new_command:
				new_command = (new_command).replace(arg,a.lower())
		new_command = new_command.replace('(','')
		new_command = new_command.replace(')','')
		new_command = re.sub(r'\]+',']',new_command)
		new_command = re.sub(r'\[+','[',new_command)

		new_all_commands.append([index,new_command])
	
	with open(filename,'w') as csvwrite:
		writer = csv.writer(csvwrite)
		writer.writerows(new_all_commands)


#Counts the number of examples for each command (by looking at the label)
def count_examples(filename):
	all_commands = list(csv.reader(open(filename)))
	count_list = [0]*(int(all_commands[-1][0]))
	for command in all_commands:
		num =  int(command[0]) - 1
		count_list[num] += 1

	for i,n in enumerate(count_list):
		print("Command {} has {} variants".format(i+1,n))


#Stupid command - I wanted to see if replacing [pictures of myself] to [photos of myself] would impact performance
#because another classifier depended a lot on the word "pictures". It didn't. 
def process_out_pictures(filename,filename2):
	all_commands = list(csv.reader(open(filename)))
	all_new_commands = []
	for command in all_commands:
		new_command = command
		if command[0] == str(32):
			new_command[1] = new_command[1].replace("pictures","photos")
		all_new_commands.append(new_command)
	with open(filename2,'w') as csvfile:
		writer = csv.writer(csvfile)
		writer.writerows(all_new_commands)



def main():
	#sort_commands("commands_all_50.csv")
	#smarter_make_sklearn_file('70_vars_50_coms.csv','sklearn_70_vars_50_coms.csv')
	#normalize_commands('sklearn_70_vars_50_coms.csv')
	#sort_commands('sklearn_70_vars_50_coms.csv')
	#count_examples('sklearn_70_vars_50_coms.csv')
	#process_out_pictures('sklearn_70_vars_50_coms.csv','temp.csv')
	#shuffle_rows('temp.csv')




if __name__ == "__main__":
	main()

