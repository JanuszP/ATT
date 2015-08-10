import os

IN_DIR = 'text_cleaned'

big_langs = ['pl', 'en', 'ge', 'it', 'hr', 'lt', 'po', 'sp', 'fr']

for lang in big_langs:
    words = {}
    i = 0
    filenames = os.listdir(os.path.join(IN_DIR, lang))
    for filename in filenames:
        try:
            text = open(os.path.join(IN_DIR, lang, filename)).read()
        except:
            continue

        text = text.replace('(', ' ( ')
        text = text.replace(')', ' ) ')
        text = text.replace('[', ' [ ')
        text = text.replace(']', ' ] ')
        text = text.replace('"', ' " ')
        text = text.replace('\n', ' ')
        text = text.replace('\t', ' ')
        parenthesis_depth = 0

        for word in text.split(' '):
            if not word:
                continue

            if word in ['(', '[']:
                parenthesis_depth += 1
                continue

            if word in [')', ']']:
                parenthesis_depth -= 1
                continue
        
            word = word.strip()

            if parenthesis_depth == 0 and (word.endswith('.') or word.endswith('!') or word.endswith('?')):
                word = word[:-1]

                if word.endswith('.'):
                  on_end = False
                  word = word.rstrip('.')
                else:
                  on_end = True
            else:
                on_end = False

            if word not in words:
                words[word] = {'on_end': 0, 'not_on_end': 0}

            if on_end:
                words[word]['on_end'] += 1
            elif parenthesis_depth > 0:
                words[word]['not_on_end'] += 5
            else:
                words[word]['not_on_end'] += 1

        if parenthesis_depth > 0:
            print("Nonzero parenthesis_depth after EOF")
        i += 1
        print("status: %d/%d %s" % (i, len(filenames), filename))

    output = open('sentence_stops_analyze_' + lang, 'w')
    for word in words.keys():
        ratio = 1.0 * words[word]['on_end'] / (words[word]['on_end'] + words[word]['not_on_end'])
        if ratio >= 0.8 and (words[word]['on_end'] + words[word]['not_on_end']) > 2:
            output.write(word + '\n')
