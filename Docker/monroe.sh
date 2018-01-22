#!/bin/bash

CONTAINER=jonakarl/monroe-cli
DATA_CONTAINER=monroe-cli-data
COMMAND=$1

if [ "${COMMAND}" == "setup" ]
then
	cert_path=$2
	results_dir=$3
    if [[ "${results_dir}" == "" || "${cert_path}" == "" ]]
    then
        echo "usage : monroe.sh setup <cert_path> <results_path>"
        exit 1
    fi
    docker rm ${DATA_CONTAINER} >& /dev/null
	docker create -v ${results_dir}:/results --name ${DATA_CONTAINER} ${CONTAINER} >& /dev/null
	docker run -it --volumes-from=${DATA_CONTAINER} -v ${cert_path}:/cert.p12 ${CONTAINER} setup /cert.p12
else
    results_dir=$(docker inspect ${DATA_CONTAINER} 2> /dev/null |jq -r '.[].Mounts[] | select(.Destination=="/results") | .Source')
    if [ "${results_dir}" == "" ]
    then
        echo "Need to first run monroe.sh setup <cert_path> <results_path>"
        exit 1
    fi
    if [ "${COMMAND}" == "results" ]
    then
        echo "Results mounted on : ${results_dir}"
    fi
    docker run -it --volumes-from=${DATA_CONTAINER} ${CONTAINER} $*
fi
