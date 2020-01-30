# tellread_format_conversion
Simple scripts for manipulating the format of the TELL-Read pipeline's output sequence files

All scripts can be run through the Linux command line.

## Contents

### `add_tellread_index_to_fastq.py`
Adds the index sequences (output by the TELL-Read pipeline as a separate FastQ file) to the 
comment line of the R1 and R2 FastQ files.

#### Dependencies
- python >= 3
- scikit-bio >= 0.5.4

#### Installation
First, add the script to your `PATH`. 
Then, install all dependencies. If using conda:
```bash
conda create -n add_tellread_index_to_fastq -c anaconda \
  python=3 scikit-bio=0.5.4

conda activate add_tellread_index_to_fastq
```

#### Testing
If interested, run the automated end-to-end test with:
```bash
testing/test_add_tellread_index_to_fastq.sh \
  testing
```

#### Usage
Example usage (test data in repo):
```bash
# Assuming you are in the Github repo directory
input_dir="testing/inputs"

add_tellread_index_to_fastq.py \
  -i "${input_dir}/R1.fastq.gz" \
  -j "${input_dir}/R2.fastq.gz" \
  -k "${input_dir}/I1.fastq.gz" \
  -o "${output_dir}/${test_ID}_R1_out.fastq" \
  -p "${output_dir}/${test_ID}_R2_out.fastq"
```
run `add_tellread_index_to_fastq.py -h` for full usage instructions.

