#!/bin/bash
input_dir="data/docs"
output_dir="results"
while getopts ":i::o:" opt; do
  case ${opt} in
    i )
      input_dir=$OPTARG
      ;;
    o )
      output_dir=$OPTARG
      ;;
    : )
      echo "Invalid option: $OPTARG requires an argument" 1>&2
      ;;
  esac
done
shift $((OPTIND -1))
echo $input_dir
echo $output_dir
pip install elasticsearch
python indexing_full.py $input_dir $output_dir