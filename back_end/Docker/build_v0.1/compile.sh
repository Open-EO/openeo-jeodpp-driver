#!/bin/bash

#export DOCKER_BUILDKIT=1
export my_jeodpp_user='marlelu'
typeset -i bldn=$(cat build#) 

VERSION=$(pwd | grep -Po '[^v\_]([0-9.]+)$')

BUILD_IMAGES=()

. gitlab_token

pass_gitlab_token_as_secret_to_build_command=" \
  --secret id=gitlab_token,src=./gitlab_token \
"

# list_include_item "10 11 12" "2"
function list_include_item {
  local list="$1"
  local item="$2"
  if [[ $list =~ (^|[[:space:]])"$item"($|[[:space:]]) ]] ; then
    # yes, list include item
    return 1
  fi
  return 
}


PROGRESS_MODE=plain
PROGRESS_MODE=auto

CACHE_MODE='--no-cache'
CACHE_MODE=''

#set -xeuo pipefail
set -o pipefail

#[ "$1" ]#|| printf "No version number provided!\nes. ./compile,sh 0.10\n\n" || exit;  # if no version provided exit
VERSION=$(pwd | grep -Po '[^v\_]([0-9.]+)$')

#JEOREG="jeoreg.cidsn.jrc.it:5000/"
#REP="jeodpp-k8s/"
#IMAGE=${JEOREG}${REP}${IMG}:${VERSION}_${bldn}
#IMAGE=${JEOREG}${REP}${IMAGENAME}:${VERSION}

base_image='debian:buster'

## Building folders to be considered
NB1='01-base'
NB2='02-jupyter'
ALL_FOLDERS="$NB1 $NB2"

#BUILD_PROCESS="$NB2 $NB4 $NB5"
BUILD_PROCESS="$NB2"

TOTMINS=0
START=$(date +'%s') 

FORCEREBUILD=false
 
i=1
for nb in $ALL_FOLDERS; do
  cd $nb
  . .setting
  IMG="$target_docker_image_name:v${VERSION}"
  echo "IMAGE present in list: $(list_include_item $BUILD_PROCESS $nb) "
  if [ ! -z $(sudo docker images -q ${IMG}) ] && [ $FORCEREBUILD == false ] && [ -z $(list_include_item $BUILD_PROCESS $nb) ] ; then
    echo
    echo "If IMAGE is present on host this is its ID: $(sudo docker images -q ${IMG})"
    echo "Don't build  $IMG"
    echo
  else
    echo
    echo "Building image $IMG based on $base_image"
    BUILD="$docker_build --build-arg BASE_CONTAINER=${base_image} -t $IMG ." 
    echo $BUILD
    echo
    base_image_clean=$(echo ${base_image} | sed -e 's/\:/\_/g; s/\//\_/g;')
#    tar -pczf ${base_image_clean}-info.tar.gz .
    sleep 3
  #  eval $BUILD 2>&1 | tee $nb-build-${START}.log
    eval $BUILD 2>&1 | tee $nb-build.log
    SECS=$(($(date +'%s') - $START))
    printf "\n= $i) Building done for  $IMG - $SECS seconds ================================================\n\n"
  fi
  BUILD_IMAGES+=(${IMG} Rebuild: ${FORCEREBUILD})
  base_image=$IMG
  ((i=i+1))
  ((TOTMINS=TOTMINS+(SECS/60)))
  rm -f *-info.tar.gz
  sleep 3
  cd ..
done
echo "Minuti totali di esecuzione del Build: $TOTMINS"

#tar --exclude=./build_bkp -pczf build_bkp/${bldn}_$(date +%Y%m%d-%s)-archive.tar.gz .

#IMAGE=${JEOREG}${REP}${IMG}:${VERSION}_${bldn}

eval "sudo docker tag $IMG ${JEOREG}${REP}${IMG}"

echo $((${bldn}+1)) > build#

echo "Working on these images:"
for each in "${BUILD_IMAGES[@]}"; do echo "$each"; done
echo
echo "Final image tag: ${JEOREG}${REP}${IMG}"
echo "sudo docker push ${JEOREG}${REP}${IMG}"

