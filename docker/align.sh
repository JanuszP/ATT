#!/bin/bash
BASE_DIR=/
ATT_DIR=${BASE_DIR}/att
CONF_DIR=${BASE_DIR}/conf
DICT_CONF=${CONF_DIR}/common/dictionary_docker.yml
CORP_CONF=${CONF_DIR}/common/corpus_docker.yml

OUTPUT_DIR=${BASE_DIR}/output
LOG_FILE=${BASE_DIR}/output/alignment.log

if [ -z "$SPLIT_PARTS" ]; then
    echo "Need to set SPLIT_PARTS in environment"
    exit 1
fi  

if [ -z "$SPLIT_PART_NUMBER" ]; then
    echo "Need to set SPLIT_PART_NUMBER in environment"
    exit 1
fi  

#SPLIT_PARTS=4

. ${ATT_DIR}/venv/bin/activate

## first parameter is a path to an aligner
## second parameter is an output directory
## 
function doAlignWithAligner() {
	ALIGNER_CONF=$1
	ALIGNER_OUTPUT_DIR=$2
	install -d ${ALIGNER_OUTPUT_DIR}

# 	for i in $(seq 1 ${SPLIT_PARTS}); do 
		echo python ${ATT_DIR}/align.py --dictionary ${DICT_CONF} --aligner_configuration ${ALIGNER_CONF} --corpus ${CORP_CONF} --output_folder ${ALIGNER_OUTPUT_DIR} -vvv --split_parts ${SPLIT_PARTS} --split_part_number ${SPLIT_PART_NUMBER}
		python ${ATT_DIR}/align.py --dictionary ${DICT_CONF} --aligner_configuration ${ALIGNER_CONF} --corpus ${CORP_CONF} --output_folder ${ALIGNER_OUTPUT_DIR} -vvv --split_parts ${SPLIT_PARTS} --split_part_number ${SPLIT_PART_NUMBER} 

#	done
#	wait

}

#for ALIGNER in `ls -1 ${CONF_DIR}/aligners`; do
#	echo `date` "Aligning with aligner: $ALIGNER" >> $LOG_FILE
#	doAlignWithAligner "${CONF_DIR}/aligners/${ALIGNER}" "${OUTPUT_DIR}/${ALIGNER}"
#done

# align with aligner for all supported languages
ALIGNER="aligner_de_en_es_fr_hr_it_la_pl_pt.yml"
doAlignWithAligner "${CONF_DIR}/aligners/${ALIGNER}" "${OUTPUT_DIR}/${ALIGNER}"

