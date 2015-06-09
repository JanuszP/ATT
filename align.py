#!/usr/bin/python

import os
import math
import sys
import nltk
import argparse
from att.utils import Average
from att.aligner import AlignerFactory
from att.dictionary import DictionaryFactory
from att.eta_clock import ETAClock
from att.html import CopyDependencies
from att.utils import MkdirIfNotExists, StripNonFilenameCharacters
from att.log import LogDebug, LogInfo
from att.pickle import LoadFromFile
from att.corpus import CorpusFactory
from att.global_context import global_context

def main():
  parser = argparse.ArgumentParser(description='Align a multilingual corpus'
                                               ' and write the output in the'
                                               ' TMX format.')
  parser.add_argument('--dictionary',
                      help="The location of the aligner dictionary.",
                      required=True)
  parser.add_argument('--trained_aligner',
                      help="Trained aligner (written by train.py) to load.")
  parser.add_argument('--aligner_configuration',
                      help="Configuration of an aligner that doesn't require"
                           " training.")
  parser.add_argument('--corpus',
                      help="The corpus that you want to be aligned.",
                      required=True)
  parser.add_argument('--output_folder',
                      help="The location of the alignment output.",
                      required=True)
  parser.add_argument('--min_languages',
                      help="Minimum number of languages in a document to align it.",
                      default=1)
  parser.add_argument('--length_difference_threshold',
                      help="If |min document length - max document length| > |average document length| * " +
                           "length_difference_threshold, the document will be ignored.",
                      default=None)
  parser.add_argument('--split_parts',
                      help="Number of parts into which aligned documents should be splitted.",
                      default=1)
  parser.add_argument('--split_part_number',
                      help="Number of split part.",
                      default=1)
  parser.add_argument('--verbose', '-v',
                      action='count',
                      default=0,
                      help="Determines verbosity level (none, -v, -vv or"
                           " -vvv). none: prints errors/warnings (default),"
                           " -v - prints basic information, -vv: prints debug"
                           " data, -vvv: prints everything.")
  args = parser.parse_args(sys.argv[1:])
  global_context.SetArgs(args)

  current_directory = os.path.dirname(__file__)
  nltk.data.path.append(os.path.join(current_directory, "venv/nltk_data"))

  LogDebug("[align.py] loading corpus...")
  corpus = CorpusFactory.MakeFromFile(args.corpus)
  LogDebug("[align.py] loading dictionary...")
  dictionary = DictionaryFactory.MakeFromFile(args.dictionary)
  LogDebug("[align.py] loading aligner...")
  if args.trained_aligner:
    try:
      aligner = LoadFromFile(args.trained_aligner)
    except Exception, e:
      print "Unable to load trained aligner. Perhaps you supplied an aligner"
      print "configuration file instead? Use --aligner_configuration to load"
      print "aligner configuration file."

      raise e
  elif args.aligner_configuration:
    try:
      aligner = AlignerFactory.MakeFromFile(args.aligner_configuration)
    except Exception, e:
      print "Unable to load aligner configuration file. Perhaps you supplied"
      print "a trained aligner instead? Use --trained_aligner to align with a"
      print "previously trained aligner."

      raise e
  else:
    assert(False)

  if int(args.split_parts) < 1 or int(args.split_part_number) < 1 or int(args.split_parts) < int(args.split_part_number):
    raise Exception("Invalid values for either split_parts (%s) should be >= 1 or split_part_number (%s) should be <= split_parts and >= 1" % (args.split_parts, args.split_part_number))

  splitParts = int(args.split_parts)
  splitPartNumber = int(args.split_part_number)

  LogDebug("[align.py] signal states:")
  for signal in aligner.GetSignals():
    signal.LogStateDebug()

  MkdirIfNotExists(args.output_folder)
  allIdentifiers = list(corpus.GetMultilingualDocumentIdentifiers())
  allIdentifiers.sort()

  partSize = int( math.ceil( float( len(allIdentifiers) ) / splitParts ) )

  identifiers = allIdentifiers[ (splitPartNumber - 1) * partSize : splitPartNumber * partSize ]


  LogDebug("[align.py] %d document(s) to align..." % len(identifiers))
  eta_clock = ETAClock(0, len(identifiers), "Aligning corpus")
  verifications = []
  docNumber = 0
  for identifier in identifiers:
    eta_clock.Tick()
    docNumber += 1
    output_path = os.path.join(
        args.output_folder,
        '%s.tmx' % StripNonFilenameCharacters(identifier))

    mdoc = corpus.GetMultilingualDocument(identifier)

    LogDebug("[align.py] %d of %d, aligning document %s, languages: %s", docNumber, len(identifiers), identifier, mdoc.GetLanguages())

    alignerDocMatchingLanguages = 0
    for alignerLang in aligner.GetLanguages():
      for docLang in mdoc.GetLanguages():
        if alignerLang == docLang:
          alignerDocMatchingLanguages += 1
          break

    if alignerDocMatchingLanguages < 2:
      LogDebug("[align.py] skipping document %s, not enough languages, aligner supports: %s, document has: %s" % (identifier, aligner.GetLanguages(), mdoc.GetLanguages()))
      continue

    lengths = [mdoc.NumSentences(language) for language in mdoc.GetLanguages()]

    if args.length_difference_threshold:
      if (max(lengths) - min(lengths)) / Average(lengths) > float(args.length_difference_threshold):
        LogInfo("[align.py] max_length=%s min_length=%s, ignored", max(lengths), min(lengths))
        continue

    if mdoc.NumDocuments() >= int(args.min_languages):
      aligned = aligner \
          .Align(mdoc, dictionary)
      aligner.SaveVerifications(aligned, dictionary)
      aligned.RenderTMX(identifier, output_path)
      verification, unused_scores = aligner.Verify(aligned, dictionary)
      if verification is not None:
        verifications.append(verification)
      del aligned
    else:
      LogDebug("[align.py] no documents")
    del mdoc
  if len(verifications) > 0:
    LogInfo("[align.py] average verification result: %s", Average(verifications))
  else:
    LogInfo("[align.py] average verification result not available - no verifications")
if __name__ == "__main__":
    main()
