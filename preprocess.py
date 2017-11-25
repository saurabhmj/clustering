#Get top 20 topics

import os
import re
from operator import itemgetter
directory = os.getcwd()+"/reuters21578"
pattern = re.compile("<TOPICS><D>[^(><)]*</D></TOPICS>")
count_of_topics = {}
for file in [f for f in os.listdir(directory) if f.endswith(".sgm")]:
    
    file_object = open(os.path.join(directory,file),"r").read()
    single_topics = pattern.findall(file_object)
    #print "parsing : ", os.path.join(directory,file)
    for topic in single_topics:
        
        topic = re.sub("</D></TOPICS>","",re.sub("<TOPICS><D>","",topic))
        if topic in count_of_topics:
            count_of_topics[topic] = count_of_topics[topic] + 1
        else:
            #print "topic added : ",topic
            count_of_topics[topic] = 1

#print count_of_topics

sorted_topics = sorted(count_of_topics.iteritems(), key=itemgetter(1), reverse=True)

#print "TOTAL SUM : ", sum(count_of_topics.values())
sorted_topics = sorted_topics[:20]

top20 = []

for topic in sorted_topics:
    top20.append(topic[0])

#print sorted_topics


# Parse all sgm files and preprocess them

import xml.etree.ElementTree as ET
import nltk
from nltk.tokenize import word_tokenize
from collections import Counter
from nltk.stem.porter import *
nltk.download('punkt')
all_reuters = []
porter = PorterStemmer()
all_tokens = []


for file in [f for f in os.listdir(directory) if f.endswith(".sgm")]:
    
    file_object = open(os.path.join(directory,file),"rb").read()
    #print "parsing file : ", os.path.join(directory,file)
    
    #replace the non-xml compliant strings with temporary strings
    rpl_file = file_object.replace("&","__amp__") 
    rpl_file = rpl_file.replace("#","__hash__")
    
    #attach a temporary root to parse xml, and elminate non-unicode character
    rpl_file = re.sub("<![^>]*>", "<root>", rpl_file)
    rpl_file = re.sub(u'\u00fc', "", rpl_file)
    rpl_file = rpl_file + "</root>"

    #build a document tree
    root = ET.fromstring(rpl_file)
    
    reuters = root.findall('./REUTERS')
    
    for reuter in reuters:
        topics = reuter.findall('./TOPICS/D')
        if(len(topics)==1 and (topics[0].text in top20)):

            newID = reuter.attrib["NEWID"]
            body = reuter.findall('./TEXT/BODY')
            
            if len(body)>0:
                
                bodytext = body[0].text
                
                #replace temporary strings with original values
                bodytext = re.sub('__amp__','&',bodytext)
                bodytext = re.sub('__hash__','#',bodytext)
                
                #eliminate non-ascii characters by encoding the string into ascii
                #bodytext = bodytext.encode('ascii','ignore')               
                bodytext = "".join(i for i in bodytext if ord(i)<128)
                
                #convert to lower case
                bodytext = bodytext.lower()
                
                #replace non-alphanumerics by space
                bodytext = re.sub('[^a-zA-Z0-9]+',' ', bodytext)
                
                #replace only numbers by spaces
                bodytext = re.sub('[0-9]+','', bodytext)
                
                #replace more than one spaces by single space
                bodytext = re.sub('\s(\s)+',' ', bodytext)
                
                #tokenize and find stem words using porter stemmer
                tokens = word_tokenize(bodytext)
                stemmed_tokens = [porter.stem(word) for word in tokens]
                
                #append to a list of all tokens
                all_tokens+=stemmed_tokens
                
                #make a dictionary of tokens
                stemmed_tokens_count = {}
                for key, value in Counter(stemmed_tokens).items():
                    stemmed_tokens_count[key] = value
                
                #put relevant info into a dictionary
                reuter_dict = {}
                reuter_dict['ID'] = newID
                reuter_dict['TOPIC'] = topics[0].text
                #reuter_dict['BODY'] = bodytext
                reuter_dict['TOKENIZED'] = stemmed_tokens_count
                all_reuters.append(reuter_dict)

#Count all the unique tokens in set of all documents                
all_tokens_count = Counter(all_tokens)


#Cover the tokenzied string to dictionary
all_tokens_dict = {}

for key,value in all_tokens_count.items():
    if value >= 5:
        all_tokens_dict[key] = value

#Read the stopwords
stopwordsfile = open(os.path.join(os.getcwd(),"stoplist.txt"),"r").read()

stopwords_list = stopwordsfile.split()
#print len(stopwords_list)

#Delete the stopwords
for key,value in all_tokens_dict.items():
    if key in stopwords_list:
        del all_tokens_dict[key]

#Convert to array
import numpy as np

freq_arr = np.zeros((len(all_reuters), len(all_tokens_dict)))
sqrt_arr = np.zeros((len(all_reuters), len(all_tokens_dict)))
log2_arr = np.zeros((len(all_reuters), len(all_tokens_dict)))
ones_arr = np.ones((len(all_reuters), len(all_tokens_dict)))


#Construct the frequency array
count=0

for index in range(0,len(all_reuters)):
    curr_tokens = {key : 0 for key in all_tokens_dict.keys()}#all_reuters[index]['TOKENIZED']
    for key, value in all_reuters[index]['TOKENIZED'].items():
        if key in curr_tokens:
            curr_tokens[key] = value
    #all_reuters[index]['TOKENIZED'].clear()
    freq_arr[index] = np.fromiter(iter(curr_tokens.values()), dtype=int)

#Normalize the matrix
def normalize (matrix):
    norm_mat = np.linalg.norm(matrix,2,axis=1)
    norm_mat[norm_mat == 0] = 1
    return matrix / np.expand_dims(np.atleast_1d(norm_mat), axis =1 )

#Write normalized vectors to file
def writeToFile(filename, matrix):
    thefile = open(filename, "w")
    count=0
    #initialized = False
    #final_arr = np.array()
    for index in range(0,len(all_reuters)):
        newid = all_reuters[index]['ID']
        #from IPython.core.debugger import Tracer; Tracer()()
        for dim in range(5632):
            if matrix[index][dim] > 0.0:
                string = newid+","+str(dim)+","+str(round(matrix[index][dim],6))
                thefile.write(string+"\n")
                count = count + 1 
    return count

#Call writeToFile
writeToFile("freq.csv",normalize(freq_arr))

sqrt_arr = np.sqrt(freq_arr) + ones_arr
sqrt_arr[sqrt_arr == 1] = 0
writeToFile("sqrtfreq.csv",normalize(sqrt_arr))

log2_arr = np.log2(freq_arr) + ones_arr
log2_arr[log2_arr == (np.inf*-1)] = 0
writeToFile("log2freq.csv",normalize(log2_arr))

#Write classfile
thefile = open("reuters21578.classfile", "w")
for index in range(0,len(all_reuters)):
    stringToWrite = all_reuters[index]['ID'] + "," + all_reuters[index]['TOPIC'] + "\n"
    thefile.write(stringToWrite)
thefile.close()

#Write label file
thefile = open("reuters21578.clabel", "w")
curr_tokens = {key : 0 for key in all_tokens_dict.keys()}
for key in curr_tokens:
    thefile.write(key+"\n")
thefile.close()
