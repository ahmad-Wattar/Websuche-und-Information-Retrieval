#!/bin/bash

input_dir="data_final"
output_dir="results_final"
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
echo "$input_dir" >> input_dir.txt
echo "$output_dir" >> output_dir.txt
sudo docker build -f ./Docker/Dockerfile -t mysoft
sudo docker run -t -d --name touche mysoft
sudo docker exec -it touche /bin/bash
bash my-software-final.sh
