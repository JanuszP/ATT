import os
import sys
import nltk
import argparse
from att.pickle import SaveToFile
from att.corpus import CorpusFactory
from att.aligner import AlignerFactory
from att.global_context import global_context

def main():
  parser = argparse.ArgumentParser(description='Align a corpus.')
  parser.add_argument('--training_corpus',
                      help="The corpus our aligner will be trained on.",
                      required=True)
  parser.add_argument('--aligner',
                      help="The aligner configuration location.",
                      required=True)
  parser.add_argument('--training_set_size',
                      help="The number of documents that will be taken from"
                           " the corpus to train the aligner.",
                      default=500,
                      type=int,
                      required=True)
  parser.add_argument('--output',
                      help="The file trained aligner should be written to.",
                      required=True)
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
  print args.training_set_size
  training_corpus = CorpusFactory.MakeFromFile(args.training_corpus)
  aligner = AlignerFactory.MakeFromFile(args.aligner)
  aligner.Train(training_corpus, args.training_set_size)

  SaveToFile(aligner, args.output)

if __name__ == "__main__":
    main()
