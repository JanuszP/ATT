#!/bin/bash
BASE_DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/..
ATT_DIR=${BASE_DIR}/att
CONF_DIR=${BASE_DIR}/conf
OUTPUT_DIR=${BASE_DIR}/output
LOG_FILE=${BASE_DIR}/output/alignment.log
SPLIT_PARTS=4

source ${ATT_DIR}/venv/bin/activate

## first parameter is a path to an aligner
## second parameter is an output directory
## 
function doAlignWithAligner() {
	ALIGNER_CONF=$1
	ALIGNER_OUTPUT_DIR=$2
	install -d ${ALIGNER_OUTPUT_DIR}

 	for i in $(seq 1 ${SPLIT_PARTS}); do 
		echo python ${ATT_DIR}/align.py --dictionary ${CONF_DIR}/common/dictionary.yml --aligner_configuration ${ALIGNER_CONF} --corpus ${CONF_DIR}/common/corpus.yml --output_folder ${ALIGNER_OUTPUT_DIR} -vvv --split_parts ${SPLIT_PARTS} --split_part_number ${i} &
		python ${ATT_DIR}/align.py --dictionary ${CONF_DIR}/common/dictionary.yml --aligner_configuration ${ALIGNER_CONF} --corpus ${CONF_DIR}/common/corpus.yml --output_folder ${ALIGNER_OUTPUT_DIR} -vvv --split_parts ${SPLIT_PARTS} --split_part_number ${i} &
	done
	wait

}

#for ALIGNER in `ls -1 ${CONF_DIR}/aligners`; do
#	echo `date` "Aligning with aligner: $ALIGNER" >> $LOG_FILE
#	doAlignWithAligner "${CONF_DIR}/aligners/${ALIGNER}" "${OUTPUT_DIR}/${ALIGNER}"
#done

# align with aligner for all supported languages
ALIGNER="aligner_de_en_es_fr_hr_it_la_pl_pt.yml"
doAlignWithAligner "${CONF_DIR}/aligners/${ALIGNER}" "${OUTPUT_DIR}/${ALIGNER}"

