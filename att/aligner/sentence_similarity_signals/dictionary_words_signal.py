"""See `SentenceSimilarityAligner: available signals' in the documentation."""

import math

from att.counter import ProbabilisticCounter
from att.classifier import FastBucketAverage
from att.utils import Flatten
from nltk.tokenize import word_tokenize
from att.aligner.sentence_similarity_signals.signal import Signal
from att.aligner.sentence_similarity_signals.signal_factory import SignalFactory
from exceptions import TrainingRequiredException

@SignalFactory.Register
class DictionaryWordsSignal(Signal):
  """A signal that translates two sentences and looks for common translations
  in each one."""
  def __init__(self, config):
    super(DictionaryWordsSignal, self).__init__(config)
    self._tokenize_dict = {}

  def ProcessCorpusBeforeTraining(
      self,
      unused_languages,
      training_corpus,
      training_set_size,
      dictionary):
    """Preprocess a corpus and gather English word frequency statistics."""
    self._word_statistics = {}
    for identifier in training_corpus.GetFirstIdentifiers(training_set_size):
      multilingual_document = training_corpus.GetMultilingualDocument(
          identifier)
      for language in multilingual_document.GetLanguages():
        document = multilingual_document.GetDocument(language)
        for sentence in document.GetSentences():
          for foreign_word in word_tokenize(sentence.lower()):
            for word in dictionary.ToEnglish(language, foreign_word):
              if not word in self._word_statistics:
                self._word_statistics[word] = 0
              self._word_statistics[word] += 1

  def _MemoizedWordTokenizeAndTranslate(self, lang, sentence, dictionary):
    """Convert a sentence to a list of word translations."""
    if not sentence in self._tokenize_dict:
      words = word_tokenize(sentence.lower())
      self._tokenize_dict[sentence] = \
          frozenset(words + Flatten([dictionary.ToEnglish(lang, word)
                             for word in words]))
    return self._tokenize_dict[sentence]

  def ResetCache(self):
    """Reset the internal per-sentence cache."""
    del self._tokenize_dict
    self._tokenize_dict = {}

  def GetSimilarity(self, lang1, sentence1, lang2, sentence2, dictionary):
    """Compute the signal value."""
    words1 = self._MemoizedWordTokenizeAndTranslate(
        lang1, sentence1, dictionary)
    words2 = self._MemoizedWordTokenizeAndTranslate(
        lang2, sentence2, dictionary)
    word_score_sum = 0
    for word in words1 & words2:
      if not hasattr(self, '_word_statistics'):
        word_score_sum += 1.0
      else:
        if not word in self._word_statistics:
          word_score_sum += 1.0
        else:
          word_score_sum += 1.0 / math.log(1 + self._word_statistics[word])
    return word_score_sum / float(math.sqrt(len(sentence1) + len(sentence2)))

  def _GetAggregator(self):
    """See signal.py"""
    return FastBucketAverage(0.005, 0.5, 20)
