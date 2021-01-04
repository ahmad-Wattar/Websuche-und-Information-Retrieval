while getopts i:o: flag

if [-n "$input_dir$"] then
	do
		case "${flag}" in
			i) input_dir=${OPTARG};;
			o) output_dir=${OPTARG};;
		esac
	done


	echo $(python3 indexing_full.ipynb $input_dir $output_dir) > /dev/null

else
    do
        case "${flag}" in
            i) input_dir=${OPTARG};;
            o) output_dir=${OPTARG};;
        esac
    done
    echo $(python3 indexing_full.ipynb $input_dir $output_dir) > /dev/null
    
fi


