#!/usr/bin/env python
# add_tellread_index_to_fastq.py
# Copyright Jackson M. Tsuji, Neufeld Research Group, 2020

# Load libraries
import logging
import time
import os
import sys
import argparse
import skbio

# GLOBAL VARIABLES
SCRIPT_VERSION='0.0.1'
DEFAULT_INDEX_TAG='BC:Z'

# Set up the logger
logging.basicConfig(format="[ %(asctime)s UTC ]: %(levelname)s: %(message)s")
logging.Formatter.converter = time.gmtime
logger = logging.getLogger(__name__)


def open_output_file(output_filepath, compression='auto'):
    """
    Opens an output file for skbio with optional compression

    :param output_filepath: path to the output file (string)
    :param compression: 'auto' to determine the compression type based on the file extension
                        (.gz or .bz2). Otherwise, provide None, 'gzip', or 'bz2' to set manually.
    :return: output file handle for writing
    """
    if compression == 'auto':
        # Choose how to open the output file based on extension
        if os.path.splitext(output_filepath)[1] == '.gz':
            output_file = skbio.io.util.open(output_filepath, 'w', compression='gzip')
        elif os.path.splitext(output_filepath)[1] == '.bz2':
            output_file = skbio.io.util.open(output_filepath, 'w', compression='bz2')
        else:
            output_file = skbio.io.util.open(output_filepath, 'w')
    else:
        # Use the manually defined compression mode desired by the user
        output_file = skbio.io.util.open(output_filepath, 'w', compression=compression)
    
    return(output_file)


def add_index_to_sequence_description(fastq_record, index_sequence, comment_tag=DEFAULT_INDEX_TAG):
    """
    Add a given index sequence as a comment in a different FastQ record

    :param fastq_record: skbio Sequence Class object
    :param index_sequence: DNA sequence (string; really, any string is accepted)
    :param comment_tag: the comment tag to apply for the added sequence in the fastq_record
    :return: skbio Sequence Class object with added description
    """
    # TODO: ensure that the BC:X comment is not already in use
    fastq_description = fastq_record.metadata['description']
    
    if fastq_description == '':
        fastq_record.metadata['description'] = comment_tag + ':' + index_sequence
    else:
        fastq_record.metadata['description'] = fastq_description + ' ' + \
                                               comment_tag + ':' + index_sequence
    
    return(fastq_record)


def main(args):
    # Set user variables
    R1_filepath = args.input_R1
    R2_filepath = args.input_R2
    I1_filepath = args.input_I1
    R1_output_filepath = args.output_R1
    R2_output_filepath = args.output_R2
    fastq_type = args.fastq_type
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
    logger.info('FastQ type: ' + fastq_type)
    logger.info('Index tag: ' + index_tag)
    logger.info('Verbose logging: ' + str(verbose))
    logger.info('################')

    # Define the generators
    logger.debug("Opening input files")
    R1 = skbio.io.read(R1_filepath, format='fastq', verify=True, variant=fastq_type)
    R2 = skbio.io.read(R2_filepath, format='fastq', verify=True, variant=fastq_type)
    I1 = skbio.io.read(I1_filepath, format='fastq', verify=True, variant=fastq_type)

    # Open output files
    # TODO - stop if output files already exist. Add a '--force' flag to override.
    logger.debug("Opening output files")
    R1_out = open_output_file(R1_output_filepath)
    R2_out = open_output_file(R2_output_filepath)

    logger.debug("Beginning parsing of input files")
    for R1_record,R2_record,I1_record in zip(R1,R2,I1):
        # Check that the index, R1, and R2 sequences have the same ID
        R1_id = R1_record.metadata['id']
        if R1_id != R2_record.metadata['id'] or \
                R1_id != I1_record.metadata['id']:

            logger.error('FastQ records do not match! Exiting...')
            logger.error('R1: ' + R1_record.metadata['id'])
            logger.error('R2: ' + R2_record.metadata['id'])
            logger.error('I1: ' + I1_record.metadata['id'])
            sys.exit(1)

        index_sequence = str(I1_record)

        # Assign index sequence as the description of R1 and R2 reads
        R1_record = add_index_to_sequence_description(R1_record, index_sequence, comment_tag=index_tag)
        R2_record = add_index_to_sequence_description(R2_record, index_sequence, comment_tag=index_tag)

        # Write - hard-coded to the modern 'illumina1.8' variant
        skbio.io.write(R1_record, into=R1_out, format='fastq', variant='illumina1.8')
        skbio.io.write(R2_record, into=R2_out, format='fastq', variant='illumina1.8')

    logger.debug("Finished parsing of input files")

    # Close output files
    logger.debug("Closing output files")
    R1_out.close()
    R2_out.close()


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
    parser.add_argument('-t', '--fastq_type', required=False, default='illumina1.8',
                        help='FastQ encoding type - see scikit-bio docs (default: "illumina1.8")')
    parser.add_argument('-x', '--index_tag', required=False, default=False,
                        help='The FastQ tag for the index sequences (default: ' + DEFAULT_INDEX_TAG + ')')
    parser.add_argument('-v', '--verbose', required=False, action='store_true',
                        help='Enable for verbose logging.')

    command_line_args = parser.parse_args()
    main(command_line_args)
