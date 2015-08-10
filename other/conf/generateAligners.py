import yaml

languages = [ "de", "fr", "en", "hr", "it", "la", "pl", "pt", "es" ]
baseAlignerPath = "common/base_aligner.yml"
alignersOutputPath = "aligners"


stream = file(baseAlignerPath, 'r') 
baseAligner = yaml.load( file(baseAlignerPath, 'r') )
print baseAligner

def GenerateLanguageCombinations(lastLang, choosenLanguages, handleLanguages):
  for lang in languages:
    if lang <= lastLang: 
      continue

    choosenLanguages.append(lang)

    handleLanguages(choosenLanguages)

    GenerateLanguageCombinations(lang, choosenLanguages, handleLanguages)
    choosenLanguages.pop()

def PrintList(languagesList):
  if len(languagesList) > 1: 
    print languagesList

def GenerateAlignerForLanguages(languagesList):
  if len(languagesList) < 2: 
    return
  baseAligner["languages"] = languagesList
  alignerPath = alignersOutputPath + "/aligner_" + ('_').join(str(x) for x in languagesList) + ".yml"
  yaml.dump(baseAligner, file(alignerPath, "w"))
  print alignerPath

  
  

GenerateLanguageCombinations("", [], GenerateAlignerForLanguages)


