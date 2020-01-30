#!/usr/bin/env python
# add_tellread_index_to_fastq.py
# Copyright Jackson M. Tsuji, Neufeld Research Group, 2020

# Load libraries
import logging
import time
import os
import sys
import argparse
from Bio.SeqIO.QualityIO import FastqGeneralIterator

# GLOBAL VARIABLES
SCRIPT_VERSION='0.0.2'
DEFAULT_INDEX_TAG='BC:Z'

# Set up the logger
logging.basicConfig(format="[ %(asctime)s UTC ]: %(levelname)s: %(message)s")
logging.Formatter.converter = time.gmtime
logger = logging.getLogger(__name__)


def main(args):
    # Set user variables
    R1_filepath = args.input_R1
    R2_filepath = args.input_R2
    I1_filepath = args.input_I1
    R1_output_filepath = args.output_R1
    R2_output_filepath = args.output_R2
    index_tag = args.index_tag
    verbose = args.verbose

    # Set logger verbosity
    if verbose is True:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    # Set index tag
    if index_tag is False:
        index_tag = DEFAULT_INDEX_TAG

    # Startup messages
    logger.info('Running ' + os.path.basename(sys.argv[0]))
    logger.info('Version: ' + SCRIPT_VERSION)
    logger.info('### SETTINGS ###')
    logger.info('R1 input filepath: ' + R1_filepath)
    logger.info('R2 input filepath: ' + R2_filepath)
    logger.info('I1 input filepath: ' + I1_filepath)
    logger.info('R1 output filepath: ' + R1_output_filepath)
    logger.info('R2 output filepath: ' + R2_output_filepath)
    logger.info('Index tag: ' + index_tag)
    logger.info('Verbose logging: ' + str(verbose))
    logger.info('################')

    # Time check
    logger.debug('Checking start time')
    start_time = time.time()

    # Open the input/output files
    logger.debug('Opening input/output file handles')
    R1_handle = open(R1_filepath, 'r')
    R2_handle = open(R2_filepath, 'r')
    I1_handle = open(I1_filepath, 'r')
    R1_output_handle = open(R1_output_filepath, 'w')
    R2_output_handle = open(R2_output_filepath, 'w')

    logger.debug('Starting loop through FastQ files')
    for R1_record, R2_record, I1_record in zip(FastqGeneralIterator(R1_handle), FastqGeneralIterator(R2_handle),
                                               FastqGeneralIterator(I1_handle)):
        # Parse FastQ info
        header_R1, seq_R1, qual_R1 = R1_record
        header_R2, seq_R2, qual_R2 = R2_record
        header_I1, seq_I1, qual_I1 = I1_record

        # Check the sequence IDs match
        id_R1 = header_R1.split(' ')[0]
        id_R2 = header_R2.split(' ')[0]
        id_I1 = header_I1.split(' ')[0]

        if id_R1 != id_R1 or id_R1 != id_I1:
            logger.error('FastQ records do not match! Exiting...')
            logger.error('R1: ' + id_R1)
            logger.error('R2: ' + id_R2)
            logger.error('I1: ' + id_I1)
            sys.exit(1)

        # Add the I1 sequence to the R1/R2 header
        # TODO - check that the comment tag does not already exist in the header
        header_R1 = header_R1 + ' ' + index_tag + ':' + seq_I1
        header_R2 = header_R2 + ' ' + index_tag + ':' + seq_I1

        # Write output
        R1_output_handle.write('@{header}\n{seq}\n+\n{qual}\n'.format(
            header=header_R1, seq=seq_R1, qual=qual_R1))
        R2_output_handle.write('@{header}\n{seq}\n+\n{qual}\n'.format(
            header=header_R2, seq=seq_R2, qual=qual_R2))

    # Close the files
    logger.debug('Closing file handles')
    R1_handle.close()
    R2_handle.close()
    I1_handle.close()
    R1_output_handle.close()
    R2_output_handle.close()

    # Wrap up
    logger.debug('Checking end time')
    end_time = time.time()
    run_time = end_time - start_time
    logger.info(os.path.basename(sys.argv[0]) + ': finished after ' + str(run_time) + ' seconds.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Converts TELL-Read pipeline output files into a format usable by third-party read '
                    'cloud assemblers (e.g., cloudSPAdes, Athena). '
                    'Copyright Jackson M. Tsuji, Neufeld Research Group, 2020. '
                    'Version: ' + SCRIPT_VERSION)
    parser.add_argument('-i', '--input_R1', required=True,
                        help='The path to the input Read 1 (R1) FastQ file.')
    parser.add_argument('-j', '--input_R2', required=True,
                        help='The path to the input Read 2 (R2) FastQ file')
    parser.add_argument('-k', '--input_I1', required=True,
                        help='The path to the input Index (I1) FastQ file')
    parser.add_argument('-o', '--output_R1', required=True,
                        help='The path to the output Read 1 (R1) FastQ file')
    parser.add_argument('-p', '--output_R2', required=True,
                        help='The path to the output Read 2 (R2) FastQ file')
    parser.add_argument('-x', '--index_tag', required=False, default=False,
                        help='The FastQ tag for the index sequences (default: ' + DEFAULT_INDEX_TAG + ')')
    parser.add_argument('-v', '--verbose', required=False, action='store_true',
                        help='Enable for verbose logging.')

    command_line_args = parser.parse_args()
    main(command_line_args)
