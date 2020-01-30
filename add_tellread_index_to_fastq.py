#!/usr/bin/env python
# add_tellread_index_to_fastq.py
# Copyright Jackson M. Tsuji, Neufeld Research Group, 2020

# Load libraries
import logging
import time
import os
import sys
import gzip
import argparse
from Bio.SeqIO.QualityIO import FastqGeneralIterator

# GLOBAL VARIABLES
SCRIPT_VERSION='0.1.1'
DEFAULT_INDEX_TAG='BC:Z'

# Set up the logger
logging.basicConfig(format="[ %(asctime)s UTC ]: %(levelname)s: %(message)s")
logging.Formatter.converter = time.gmtime
logger = logging.getLogger(__name__)

def open_file_handle(filepath, mode, compression='auto', compresslevel=5):
    """
    Opens an input or output file with optional gzip compression

    :param filepath: path to the file (string)
    :param mode: set as either 'read' or 'write'. Simplified version of open() and gzip.open().
    :param compression: 'auto' to determine the compression type based on the file extension
                        (.gz). Otherwise, provide None or 'gzip' to set manually.
    :param compresslevel: integer from 0-9; 9 is highest compression, 0 is no compression; for writing
    :return: input file handle for reading text
    """
    # TODO - add .bz2 support
    if mode == 'read':
        if compression == 'auto':
            # Choose how to open the input file based on extension
            if os.path.splitext(filepath)[1] == '.gz':
                logger.debug('Read: detected file "' + filepath + '" as gzipped')
                file_handle = gzip.open(filepath, mode='rt')
            else:
                logger.debug('Read: detected file "' + filepath + '" as uncompressed')
                file_handle = open(filepath, mode='r')
        else:
            # Choose how to open the input file based on user input
            logger.debug('Read: manual specification of compression by user: "' + compression + '"')
            if compression == 'gzip':
                file_handle = gzip.open(filepath, mode='rt')
            elif compression is None:
                file_handle = open(filepath, mode='r')
            else:
                logger.error('"compression" must be set to "auto", "gzip", or None. You set "' + \
                             compression + '". Exiting...')
                sys.exit(1)

    elif mode == 'write':
        if compression == 'auto':
            # Choose how to open the output file based on extension
            if os.path.splitext(filepath)[1] == '.gz':
                logger.debug('Write: detected file "' + filepath + '" as gzipped')
                file_handle = gzip.open(filepath, mode='wt', compresslevel=compresslevel)
            else:
                logger.debug('Write: detected file "' + filepath + '" as uncompressed')
                file_handle = open(filepath, mode='w')
        else:
            # Choose how to open the output file based on user input
            logger.debug('Write: manual specification of compression by user: "' + compression + '"')
            if compression == 'gzip':
                file_handle = gzip.open(filepath, mode='wt', compresslevel=compresslevel)
            elif compression is None:
                file_handle = open(filepath, mode='w')
            else:
                logger.error('"compression" must be set to "auto", "gzip", or None. You set "' + \
                             compression + '". Exiting...')
                sys.exit(1)

    else:
        logger.error('"mode" must be either "read" or "write"; you provided "' + mode + '". Exiting...')
        sys.exit(1)

    return file_handle


def main(args):
    # Set user variables
    R1_filepath = args.input_R1
    R2_filepath = args.input_R2
    I1_filepath = args.input_I1
    R1_output_filepath = args.output_R1
    R2_output_filepath = args.output_R2
    index_tag = args.index_tag
    compresslevel = args.compression_level
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
    logger.info('Compression level (if writing gzipped files): ' + str(compresslevel))
    logger.info('Verbose logging: ' + str(verbose))
    logger.info('################')

    # Time check
    logger.debug('Checking start time')
    start_time = time.time()

    # Open the input/output files
    logger.debug('Opening input/output file handles')
    R1_handle = open_file_handle(R1_filepath, 'read')
    R2_handle = open_file_handle(R2_filepath, 'read')
    I1_handle = open_file_handle(I1_filepath, 'read')
    R1_output_handle = open_file_handle(R1_output_filepath, 'write', compresslevel=compresslevel)
    R2_output_handle = open_file_handle(R2_output_filepath, 'write', compresslevel=compresslevel)

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
    parser.add_argument('-c', '--compression_level', required=False, default=5,
                        help='Compression level for output files, if gzipped. Integer from 0-9, where 9 is highest compression and 0 is no compression (default: 5).')
    parser.add_argument('-v', '--verbose', required=False, action='store_true',
                        help='Enable for verbose logging.')

    command_line_args = parser.parse_args()
    main(command_line_args)
