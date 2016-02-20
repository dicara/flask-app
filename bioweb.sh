#!/bin/bash

declare STOP=false
declare REMOVE=false
declare UPDATE=false
declare RUN=false
declare ALL=false
declare TEST=true

declare -r BIOWEB_DEV="bioweb-api-dev"
declare -r BIOWEB_PROD="bioweb-api-prod"
declare -r BIOWEB_DEV_PORT="8020:8020"
declare -r BIOWEB_PROD_PORT="8010:8010"
declare -r STOP_PREFIX="docker stop "
declare -r REMOVE_PREFIX="docker rm "
declare -r PULL_PREFIX="docker pull swi-03.global.bio-rad.com/gbsoftware/"
declare -r ATTACH_PREFIX="docker attach --sig-proxy=false "

declare BIOWEB=$BIOWEB_DEV
declare BIOWEB_PORT=$BIOWEB_DEV_PORT

usage() {
    cat<<ENDOFUSAGE
Usage: ./$BASENAME [-p|--prod] [-s|--stop] [-v|--remove] [-u|--update] [-r|--run] [-a|--all] 
Options
    -p|--prod     Perform actions on Bioweb Prod (default is Bioweb Dev)
    -s|--stop     Stop docker image
    -v|--remove   Remove docker image
    -u|--update   Pull latest docker image
    -r|--run      Run docker image
    -a|--all      Stop, remove, pull, and run latest docker image
    -e|--execute  Execute commands (default displays commands but does not execute)
    -h|--help     Display this help
    
ENDOFUSAGE
}

if [ ! $# -gt 0 ]; then
	usage
	exit 0
fi

while [ $# -gt 0 ]; do
    case $1 in
        (-p|--prod)
            BIOWEB=$BIOWEB_PROD
            BIOWEB_PORT=$BIOWEB_PROD_PORT
            shift;;
        (-s|--stop)
            STOP=true
            shift;;
        (-v|--remove)
            REMOVE=true
            shift;;
        (-u|--update)
            UPDATE=true
            shift;;
        (-r|--run)
            RUN=true
            shift;;
        (-a|--all)
            ALL=true
            shift;;
        (-e|--execute)
            TEST=false
            shift;;
        (-h|--help)
            usage
            exit 0;;
        (*)
            usage
            exit 0;;
    esac
done

CID=$(docker ps | grep $BIOWEB | cut -d ' ' -f1)

if [[ $ALL = true || $STOP = true ]]; then
	echo $ATTACH_PREFIX $CID
	if [ ! $TEST = true ]; then
		$ATTACH_PREFIX $CID
	fi

	echo $STOP_PREFIX $CID
	if [ ! $TEST = true ]; then
		$STOP_PREFIX $CID
	fi
fi

if [[ $ALL = true || $REMOVE = true ]]; then
	echo $REMOVE_PREFIX $CID
	if [ ! $TEST = true ]; then
		$REMOVE_PREFIX $CID
	fi
fi

if [[ $ALL = true || $UPDATE = true ]]; then
	echo "docker pull swi-03.global.bio-rad.com/gbsoftware/$BIOWEB:latest"
	if [ ! $TEST = true ]; then
		docker pull swi-03.global.bio-rad.com/gbsoftware/$BIOWEB:latest
	fi
fi

if [[ $ALL = true || $RUN = true ]]; then
	echo "docker run -i -t --sig-proxy=false --name $BIOWEB -p $BIOWEB_PORT -v /mnt/bigdisk:/mnt/bigdisk -v /mnt/scratch:/mnt/scratch -v /mnt/runs:/mnt/runs:ro -v /home/bioweb/bin/blat:/bin/blat -v /etc/localtime:/etc/localtime:ro swi-03.global.bio-rad.com/gbsoftware/$BIOWEB:latest /bin/bash"
	if [ ! $TEST = true ]; then
		docker run -i -t --sig-proxy=false --name $BIOWEB -p $BIOWEB_PORT -v /mnt/bigdisk:/mnt/bigdisk -v /mnt/scratch:/mnt/scratch -v /mnt/runs:/mnt/runs:ro -v /home/bioweb/bin/blat:/bin/blat -v /etc/localtime:/etc/localtime:ro swi-03.global.bio-rad.com/gbsoftware/$BIOWEB:latest /bin/bash
	fi
fi