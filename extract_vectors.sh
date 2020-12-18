#!/usr/bin/env bash
###########################################################
# TRAIN_DIR=my_train_dir
# VAL_DIR=my_val_dir
# TEST_DIR=my_test_dir
# DATASET_NAME=my_dataset
# MAX_CONTEXTS=200
# WORD_VOCAB_SIZE=1301136
# PATH_VOCAB_SIZE=911417
# TARGET_VOCAB_SIZE=261245
# NUM_THREADS=64
PYTHON=python3



###########################################################

# TRAIN_DATA_FILE=${DATASET_NAME}.train.raw.txt
# VAL_DATA_FILE=${DATASET_NAME}.val.raw.txt
# TEST_DATA_FILE=${DATASET_NAME}.test.raw.txt

JAVA_FILES=./emos
FILE1=fn_paths.txt
FILE2=fn.txt
FILE3=paths.txt
FILE4=filtered_paths.txt
FILE5=${FILE4}.vectors
FILE6=emos_vectors.csv
EXTRACTOR_JAR=../code2vec/JavaExtractor/JPredict/target/JavaExtractor-0.0.1-SNAPSHOT.jar
DICT_PATH=/hdd/code2vec/java-large/java-large.dict.c2v
MODEL_PATH=/hdd/code2vec/code2vec/models/java-large-release/saved_model_iter3.release
EXTRACT_SCRIPT=../code2vec/JavaExtractor/extract.py
FILTER_SCRIPT=../code2vec/filter_contexts.py
CODE2VEC_SCRIPT=../code2vec/code2vec.py


rm ${FILE1} ${FILE2} ${FILE3} ${FILE4} ${FILE5}


echo "Extracting paths for each file in the directory"
${PYTHON} ${EXTRACT_SCRIPT} --jar ${EXTRACTOR_JAR} --dir ${JAVA_FILES} --ref_filename --num_threads 2 > ${FILE1}
cat ${FILE1} | cut -d' ' -f1  > ${FILE2}
cat ${FILE1} | cut -d' ' -f2- > ${FILE3}
echo "Filter contexts"
${PYTHON} ${FILTER_SCRIPT} -i ${FILE3} -o ${FILE4} -dp ${DICT_PATH}
${PYTHON} ${CODE2VEC_SCRIPT} --load ${MODEL_PATH} --test ${FILE4} --export_code_vectors
paste -d',' ${FILE2} ${FILE5} > ${FILE6}
#rm ${FILE1} ${FILE2} ${FILE3} ${FILE4} ${FILE5}

# python3 filter_contexts.py  -i paths.txt -o path_filterd.txt -dp /tmp/Downloads/java14m.dict.c2v/data/java14m/java14m.dict.c2v
# python3 ../code2vec/code2vec.py --load /hdd/code2vec/code2vec/models/java14_model/saved_model_iter8.release --test paths_filtered.txt --export_code_vectors

