#!/bin/bash


input_dir=$(<input_dir.txt)
output_dir=$(<output_dir.txt)

echo $input_dir
echo $output_dir
pip install elasticsearch
python final_version_for_tira.py $input_dir $output_dir
