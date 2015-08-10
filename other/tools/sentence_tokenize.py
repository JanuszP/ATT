# -*- coding: utf-8 -*-

from nltk.tokenize.punkt import PunktSentenceTokenizer, PunktTrainer
import os
import string

IN_DIR = 'text_cleaned'
OUT_DIR = 'out2'
LANG_SIZE_THRESHOLD = 100
# single letters, digits and numbers, digits with 'a' and some manually added words
HACK_SHORTCUTS = [
      'cf', 'por', '2tim', 'lev', '2cor', 'cor', 'io', 'col', 'matth', 'gen', \
      'vs', 'cfr', 'ev', 'ioh', 'par', 'luc', 'ps', 'act', 'sez', 'st', 'vv', \
      'v', 'gr', 'cr', 'mr'] + \
      list(string.letters) + \
      [str(x) for x in range(100)] + \
      [str(x) + 'a' for x in range(100)]

CORPUS_LANGUAGE_CODES = {
    'en': 'en',
    'fr': 'fr',
    'ge': 'de',
    'hr': 'hr',
    'it': 'it',
    'lt': 'la',
    'pl': 'pl',
    'po': 'pt',
    'sp': 'es'}
CORPUS_LANGUAGE_CODES_REVERSED = dict([(l2, l1) for (l1, l2) in CORPUS_LANGUAGE_CODES.iteritems()])

docs = {}
lang_doc_nums = {}
for lang in os.listdir(IN_DIR):
  if os.path.isdir(os.path.join(IN_DIR, lang)):
    for doc in os.listdir(os.path.join(IN_DIR, lang)):
      if os.path.isfile(os.path.join(IN_DIR, lang, doc)):
        lang_doc_nums[lang] = lang_doc_nums.get(lang, 0) + 1

        doc_name = '_'.join(doc.split('_')[:-1])
        if doc_name in docs:
          docs[doc_name].append(lang)
        else:
          docs[doc_name] = [lang]

full_texts = {}
big_langs = []
for doc_name, langs in docs.iteritems():
  for lang in langs:
    if lang_doc_nums[lang] > LANG_SIZE_THRESHOLD:
      big_langs.append(lang)
big_langs = list(set(big_langs))

big_langs = ['pl', 'en', 'ge', 'it']

sentence_stops_analyzes = {}
for lang in big_langs:
    lines = [line.strip().lower()
             for line in open('sentence_stops_analyze_' + lang).readlines()] + HACK_SHORTCUTS
    sentence_stops_analyzes[lang] = \
        lines + \
        ['(' + line
         for line in lines] + \
        ['[' + line
         for line in lines]

def tokenize(lang, text, doc_name):
    text = text.replace('\n', ' ')
    text = text.replace('\t', ' ')
    text = text.replace('”', '” ')
    text = text.replace('„', ' „')
    text = text.replace(')', ') ')
    text = text.replace('(', ' (')
    text = text.replace('|', ' | ')
    parenthesis_depth = 0
    sentence = []
    sentences = []

    i = 0
    words = [word.strip() for word in text.split(' ') if word.strip()]
    for i in range(len(words)):
        word = words[i]

        sentence.append(word)

        if word.endswith('.'):
            n_word = word[:-1]
            if n_word.endswith('.'):
                end_sentence = False
            elif n_word.lower() in sentence_stops_analyzes[lang]:
                end_sentence = False
            elif set(n_word.lower()) & set(string.letters) == set([]):
                end_sentence = False
            else:
                end_sentence = True
        elif word.endswith('?') or word.endswith('!'):
            end_sentence = True
        else:
            end_sentence = False

        if (word == '|') or \
           (end_sentence and i < len(words) - 1 and words[i + 1][0] == words[i + 1][0].upper()) or \
           (word == '.' and i > 0 and words[i - 1].endswith(')') and i < len(words) - 1 and words[i + 1][0] == words[i + 1][0].upper()):
            if len(sentence) > 0:
                sentences.append(' '.join(sentence))
            sentence = []
    if len(sentence) > 0:
        sentences.append(' '.join(sentence))
    return sentences


for doc_name, langs in docs.iteritems():
    texts = {}
    good_doc_langs = [lang for lang in langs if lang in big_langs]
    if len(good_doc_langs) > 1:
        os.makedirs(os.path.join(OUT_DIR, doc_name))
        for lang in good_doc_langs:
            f = open(os.path.join(OUT_DIR, doc_name, CORPUS_LANGUAGE_CODES[lang]), 'w')
            sentences = tokenize(lang, open(os.path.join(IN_DIR, lang, '%s_%s.txt' % (doc_name, lang))).read(), doc_name)
            for sent in sentences:
                f.write(sent.replace('\r', ' ').replace('\n', ' ') + '\n')
            f.close()
