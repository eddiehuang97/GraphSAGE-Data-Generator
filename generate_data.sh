#!/bin/sh

TMP_DIR=tmp
NUM_NODES=1000
NUM_EDGES=10
PREFIX=data

cd example_data

while [ "$1" != "" ]; do
    PARAM=`echo $1 | awk -F= '{print $1}'`
    VALUE=`echo $1 | awk -F= '{print $2}'`
    case $PARAM in
        --nodes)
            NUM_NODES=$VALUE
            ;;
        --edges)
            NUM_EDGES=$VALUE
            ;;
        --prefix)
            PREFIX=$VALUE
            ;;
    esac
    shift
done

rm -rf ${TMP_DIR}
mkdir ${TMP_DIR}

python DataGenerator.py --nodes=${NUM_NODES} --edges=${NUM_EDGES} --prefix=${PREFIX}

cat ${TMP_DIR}/class_map_first.json ${TMP_DIR}/*-class_map.json ${TMP_DIR}/class_map_second.json > ${PREFIX}-class_map.json
cat ${TMP_DIR}/G_first.json ${TMP_DIR}/*-G_node.json ${TMP_DIR}/G_second.json ${TMP_DIR}/*-G_edge.json ${TMP_DIR}/G_third.json > ${PREFIX}-G.json

rm -rf ${TMP_DIR}

cd ../graphsage

python utils.py ../example_data/${PREFIX}-G.json ../example_data/${PREFIX}-walks.txt