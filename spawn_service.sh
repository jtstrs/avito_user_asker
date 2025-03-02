#!/bin/bash

REDIS_HOST=""
REDIS_PORT=""
MONGO_HOST=""
MONGO_PORT=""

usage() {
    echo "Usage: $0  -r REDIS_HOST -p REDIS_PORT -a MONGO_HOST -b MONGO_PORT"
    exit 1
}

while getopts ":r:p:a:b:" opt; do
    case ${opt} in
        r )
            REDIS_HOST="$OPTARG"
            ;;
        p )
            REDIS_PORT="$OPTARG"
            ;;
        a )
            MONGO_HOST="$OPTARG"
            ;;
        b )
            MONGO_PORT="$OPTARG"
            ;;
        \? )
            usage
            ;;
        : )
            echo "Error: Option -$OPTARG required."
            usage
            ;;
    esac
done

if [ -z "$REDIS_HOST" ] || [ -z "$REDIS_PORT" ] || [ -z "$MONGO_HOST" ] || [ -z "$MONGO_PORT" ]; then
    usage
fi

docker run -e REDIS_HOST="${REDIS_HOST}" \
           -e REDIS_PORT="${REDIS_PORT}" \
           -e MONGO_HOST="${MONGO_HOST}" \
           -e MONGO_PORT="${MONGO_PORT}" \
           --network host \
           avito_user_asker_service