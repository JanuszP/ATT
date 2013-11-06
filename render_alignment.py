import os
import sys
import nltk
import argparse
from att.html import CopyDependencies
from att.utils import MkdirIfNotExists, StripNonFilenameCharacters
from att.log import LogDebug
from att.pickle import LoadFromFile
from att.corpus import CorpusFactory
from att.global_context import global_context

def main():
  parser = argparse.ArgumentParser(description='Render an alignment to HTML.')
  parser.add_argument('--trained_aligner',
                      help="Trained aligner (written by train.py) to load.",
                      required=True)
  parser.add_argument('--corpus',
                      help="The corpus that you want to be aligned.",
                      required=True)
  parser.add_argument('--output_folder',
                      help="The location of the alignment output.",
                      required=True)
  parser.add_argument('--verbose', '-v',
                      action='count',
                      default=0,
                      help="Determines verbosity level (-v, -vv or -vvv):"
                           " 0 - prints errors/warnings (default),"
                           " 1 - prints information, 2 - prints everything.")

  args = parser.parse_args(sys.argv[1:])
  global_context.SetArgs(args)

  current_directory = os.path.dirname(__file__)
  nltk.data.path.append(os.path.join(current_directory, "venv/nltk_data"))

  LogDebug("[render_alignment.py] loading corpus...")
  corpus = CorpusFactory.MakeFromFile(args.corpus)
  LogDebug("[render_alignment.py] loading aligner...")
  aligner = LoadFromFile(args.trained_aligner)
  LogDebug("[render_alignment.py] aligning and rendering...")
  MkdirIfNotExists(args.output_folder)
  for identifier in corpus.GetMultilingualDocumentIdentifiers():
    output_path = os.path.join(
        args.output_folder,
        'doc_%s.html' % StripNonFilenameCharacters(identifier))
    aligner \
        .Align(corpus.GetMultilingualDocument(identifier)) \
        .RenderHTML(identifier, output_path)
    CopyDependencies(['common.css', 'alignment_render.css'], args.output_folder)

if __name__ == "__main__":
    main()