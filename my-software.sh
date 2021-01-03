while getopts i:o: flag
do
    case "${flag}" in
        i) input_dir=${OPTARG};;
        o) output_dir=${OPTARG};;
    esac
done


echo $(python3 indexing_full.ipynb $input_dir $output_dir) > /dev/null
