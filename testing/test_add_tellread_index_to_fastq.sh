#!/usr/bin/env bash
set -euo pipefail
# test_add_tellread_index_to_fastq.sh
# Copyright Jackson M. Tsuji, 2020
# End-to-end test for add_tellread_index_to_fastq.py

# GLOBAL variables
readonly SCRIPT_NAME="${0##*/}"
FAILED_TESTS=0

#######################################
# Compares two MD5 hashes for the same file in HARD-CODED output dirs
# Globals:
#   FAILED_TESTS: count of failed tests
# Arguments:
#   input_basename: the basename (no directory, no extension) of the desired MD5 hashes to test between the outputs and expected_outputs folders
# Returns:
#   updates FAILED_TESTS
#######################################
function check_md5s() {
  # User-provided inputs
  local input_basename
  input_basename=$1

  # TODO - maybe set output and expected_outputs dirs as GLOBAL
  md5_expected=$(cat "${expected_outputs_dir}/${input_basename}.fastq.md5" | cut -d " " -f 1)
  md5_actual=$(cat "${output_dir}/${input_basename}.fastq.md5" | cut -d " " -f 1)

  if [[ "${md5_expected}" != "${md5_actual}" ]]; then
    echo "[ $(date -u) ]: '${input_basename}.tsv': FAILED: Actual hash does not match expected hash"
    FAILED_TESTS=$((${FAILED_TESTS}+1))
  else
    echo "[ $(date -u) ]: '${input_basename}.tsv': PASSED"
  fi
}

# If no input is provided, provide help and exit
if [[ $# -eq 0 ]]; then
  echo "No arguments provided. Please run '-h' or '--help' to see help. Exiting..." >&2
  exit 1
elif [[ $1 = "-h" ]] || [[ $1 = "--help" ]]; then

  # Help statement
  printf "${SCRIPT_NAME}: run end-to-end test for tellread_format_convertor.py\n"
  printf "Copyright Jackson M. Tsuji, Neufeld Research Group, 2020\n\n"
  printf "Usage: ${SCRIPT_NAME} test_dir\n\n"
  printf "Positional arguments (required):\n"
  printf "   test_dir: path to the test directory containing the 'inputs' and 'outputs_expected' test folders\n\n"
  printf "Note: script will give an exit status of 1 if any tests fail; otherwise exit status will be 0.\n\n"

  # Exit
  exit 0
fi

### Get user inputs
test_dir=$1

echo "[ $(date -u) ]: Running ${SCRIPT_NAME}"
echo "[ $(date -u) ]: Test dir: '${test_dir}'"

### Expected positions of folders
input_dir="${test_dir}/inputs"
expected_outputs_dir="${test_dir}/outputs_expected"
output_dir="${test_dir}/outputs" # should NOT yet exist!

### Look for dirs
if [[ ! -d "${input_dir}" ]]; then
  echo "[ $(date -u) ]: ERROR: did not find input dir at '${input_dir}'. Exiting..."
  exit 1
elif [[ ! -d "${expected_outputs_dir}" ]]; then
  echo "[ $(date -u) ]: ERROR: did not find expected outputs dir at '${expected_outputs_dir}'. Exiting..."
  exit 1
fi

### Create the output dir
if [[ -d "${output_dir}" ]]; then
  echo "[ $(date -u) ]: ERROR: output directory '${output_dir}' already exists. Please specify an output dir that does not exist. Exiting..."
  exit 1
else
  mkdir "${output_dir}"
fi

## Test 1
test_ID="01_standard"
echo "[ $(date -u) ]: Running script on test data '${test_ID}'"
set +e
add_tellread_index_to_fastq.py \
  -i "${input_dir}/R1.fastq" \
  -j "${input_dir}/R2.fastq" \
  -k "${input_dir}/I1.fastq" \
  -o "${output_dir}/${test_ID}_R1_out.fastq" \
  -p "${output_dir}/${test_ID}_R2_out.fastq" \
  > "${output_dir}/${test_ID}.log" 2>&1
run_status=$?
set -e

# If something goes wrong, print a log
if [ "${run_status}" -ne 0 ]; then
  echo "[ $(date -u) ]: ERROR: 'add_tellread_index_to_fastq.py' failed. Log info is pasted below. Exiting..."
  printf "\n\n"

  cat "${output_dir}/${test_ID}.log"

  exit 1
fi

# Generate MD5 hash of output
cat "${output_dir}/${test_ID}_R1_out.fastq" | md5sum > "${output_dir}/${test_ID}_R1_out.fastq.md5"
cat "${output_dir}/${test_ID}_R2_out.fastq" | md5sum > "${output_dir}/${test_ID}_R2_out.fastq.md5"

# Compare
check_md5s "${test_ID}_R1_out"
check_md5s "${test_ID}_R2_out"

## Test 2
test_ID="02_gzip"
echo "[ $(date -u) ]: Running script on test data '${test_ID}'"
set +e
add_tellread_index_to_fastq.py \
  -i "${input_dir}/R1.fastq.gz" \
  -j "${input_dir}/R2.fastq.gz" \
  -k "${input_dir}/I1.fastq.gz" \
  -o "${output_dir}/${test_ID}_R1_out.fastq.gz" \
  -p "${output_dir}/${test_ID}_R2_out.fastq.gz" \
  > "${output_dir}/${test_ID}.log" 2>&1
run_status=$?
set -e

# If something goes wrong, print a log
if [ "${run_status}" -ne 0 ]; then
  echo "[ $(date -u) ]: ERROR: 'add_tellread_index_to_fastq.py' failed. Log info is pasted below. Exiting..."
  printf "\n\n"

  cat "${output_dir}/${test_ID}.log"

  exit 1
fi

# Unzip outputs
gunzip "${output_dir}/${test_ID}_R1_out.fastq.gz" "${output_dir}/${test_ID}_R2_out.fastq.gz"

# Generate MD5 hash of output
cat "${output_dir}/${test_ID}_R1_out.fastq" | md5sum > "${output_dir}/${test_ID}_R1_out.fastq.md5"
cat "${output_dir}/${test_ID}_R2_out.fastq" | md5sum > "${output_dir}/${test_ID}_R2_out.fastq.md5"

# Compare
check_md5s "${test_ID}_R1_out"
check_md5s "${test_ID}_R2_out"

### Overall status
if [[ "${FAILED_TESTS}" -eq 0 ]]; then
  echo "[ $(date -u) ]: All tests PASSED. Deleting output folder."
  rm -r "${output_dir}"
  echo "[ $(date -u) ]: Testing complete."
  exit 0
else
  echo "[ $(date -u) ]: ${FAILED_TESTS} test(s) FAILED. See above log for details. Keeping outputs dir for reference. Testing complete."
  exit 1
fi
