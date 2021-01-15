#!/bin/bash

# Main in bottom

YELLOW='\033[1;33m'
BROWN='\033[0;33m'
GREEN='\033[1;32m'
RED='\033[1;31m'
NC='\033[0m' # No Color

function log {
    echo -e "\n${YELLOW}[$(date +'%H:%M:%S')]${BROWN} $ $1${NC}"
}

function loggood {
    echo -e "\n${YELLOW}[$(date +'%H:%M:%S')]${GREEN} $ $1${NC}"
}

function logerror {
    echo -e "\n${RED}[$(date +'%H:%M:%S')]${RED} $ $1${NC}"
    exit 1
}


dev=""
devext=""
if [ "$1" = "-d" ]; then
    dev="-dev"
    devext=".dev"
fi

log "creating debug file"
cp src/debug.js.sample src/debug.js
log "building frontend_app_thread"
yarn run buildoptimized$dev  && loggood "success" || logerror "some error"
log "copying built file to frontend/"
cp dist/thread.app$devext.js ../frontend/dist/app/thread.app.js && loggood "success" || logerror "some error"
log "copying en translation.json"
cp i18next.scanner/en/translation.json ../frontend/dist/app/thread_en_translation.json && loggood "success" || logerror "some error"
log "copying fr translation.json"
cp i18next.scanner/fr/translation.json ../frontend/dist/app/thread_fr_translation.json && loggood "success" || logerror "some error"
log "copying pt translation.json"
cp i18next.scanner/pt/translation.json ../frontend/dist/app/thread_pt_translation.json && loggood "success" || logerror "some error"
