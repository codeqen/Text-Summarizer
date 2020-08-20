from __future__ import print_function
import array
import string
import operator

import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.probability import FreqDist
from flask import Flask, render_template, request, redirect

import os

import bs4 as bs 
import urllib.request
from urllib.request import urlopen


import Image
from pytesseract import image_to_string

from gensim.summarization.summarizer import summarize



class summarize:

	def get_summary(self, input, max_sentences):
		sentences_original = sent_tokenize(input)

		if (max_sentences > len(sentences_original)):
			print ("Error, number of requested sentences exceeds number of sentences inputted")
		s = input.strip('\t\n')
		
		words_chopped = word_tokenize(s.lower())
		
		sentences_chopped = sent_tokenize(s.lower())

		stop_words = set(stopwords.words("english"))
		punc = set(string.punctuation)

		filtered_words = []
		for w in words_chopped:
			if w not in stop_words and w not in punc:
				filtered_words.append(w)
		total_words = len(filtered_words)
		
		word_frequency = {}
		output_sentence = []

		for w in filtered_words:
			if w in word_frequency.keys():
				word_frequency[w] += 1.0
			else:
				word_frequency[w] = 1.0 

		
		for word in word_frequency:
			word_frequency[word] = (word_frequency[word]/total_words)

		#word processing
		tracker = [0.0] * len(sentences_original)
		for i in range(0, len(sentences_original)):
			for j in word_frequency:
				if j in sentences_original[i]:
					tracker[i] += word_frequency[j]

		#priority given to weighted sentence...
		for i in range(0, len(tracker)):
			
			#weighted freq.
			index, value = max(enumerate(tracker), key = operator.itemgetter(1))
			if (len(output_sentence)+1 <= max_sentences) and (sentences_original[index] not in output_sentence): 
				output_sentence.append(sentences_original[index])
			if len(output_sentence) > max_sentences:
				break
			
			tracker.remove(tracker[index])
		
		sorted_output_sent = self.sort_sentences(sentences_original, output_sentence)
		return (sorted_output_sent)

	def sort_sentences (self, original, output):
		sorted_sent_arr = []
		sorted_output = []
		for i in range(0, len(output)):
			if(output[i] in original):
				sorted_sent_arr.append(original.index(output[i]))
		sorted_sent_arr = sorted(sorted_sent_arr)

		for i in range(0, len(sorted_sent_arr)):
			sorted_output.append(original[sorted_sent_arr[i]])
		print (sorted_sent_arr)
		return sorted_output

#Flask#

app = Flask(__name__)
@app.route('/templates', methods=['POST'])
def original_text_form():
	title = "Summarizer"
	text = request.form['input_text'] #Get text from html
	max_value = sent_tokenize(text)
	num_sent = int(request.form['num_sentences']) #Get number of sentence required in summary
	sum1 = summarize()
	summary = sum1.get_summary(text, num_sent)
	print (summary)
	return render_template("index.html", title = title, original_text = text, output_summary = summary, num_sentences = max_value)


@app.route('/ocrs_template', methods=['POST','GET'])
def original_img_form():
	f=request.files['pic']
	f.save(f.filename)
	title = "OCRS"
	# img = request.files['f.filename'] #Get text from html
	# img_opened=Image.open(img)
	
	text=image_to_string(Image.open(f.filename))
	text=text.replace("\n\n","!@#$")
	text=text.replace("\n", " ")
	text=text.replace("!@#$", "\n")
	text=text.replace("\n", " ")
	text_summary=summarize().get_summary(text, 100)
	# return render_template("index.html", title = title, original_img = img, output_text = text)
	# return render_template("index.html", name=f.filename)
	return render_template("index.html", title = title,  output_text = text, output_text_summary=text_summary)

@app.route('/')
def homepage():
	title = "Text Summarizer"
	return render_template("index.html", title = title)
	
if __name__ == "__main__":
	app.debug = True
	app.run()
