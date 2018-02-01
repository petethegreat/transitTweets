#!/bin/bash

# buildimages.sh
# build docker images for transit tweet project

# don't want to be keeping seperate "docker" versions of base code around, 
# so will copy needed files to container directories, build container, 
# then clean up as needed
# guess I could have used make or cmake for this...



# sort out the directory that we're in
executable=$0
startdir=$(pwd)

#move to the docker directory (where this script is located)
dockerdir=${executable%/*.sh}
cd $dockerdir
# get absolute path
dockerdir=$(pwd)
# get repo root path
rootdir=${dockerdir%/docker*}

# check
echo "dockerdir: ${dockerdir}"
echo "rootdir: ${rootdir}"
echo "startdir: ${startdir}"

# function to build the streamContainer image
function build_streamContainer {
    #move to dockerdir, work from there
    cd $dockerdir
    echo "building streamContainer"
    container_dir="streamContainer"
    # check directory exists
    if [ ! -d ${container_dir} ]
        then 
            echo "Error, ${dockerdir}/${container_dir} directory does not exist"
            cd $startdir
            exit
    fi


    cd ${dockerdir}/${container_dir}
    echo "in container directory $(pwd)"

    #copy code needed for this container
    tfname="TransitTweeter.py"
    tdirname="ttweeter"
    transitfile="${rootdir}/${tfname}"
    ttweeterdir="${rootdir}/${tdirname}"
    # check these exist
    if [ ! -f $transitfile ]
        then
            echo "error, file ${transitfile} not found, exiting"
            cd $startdir
            exit
    fi
    if [ ! -d $ttweeterdir ]
        then
            echo "error, directory ${ttweeterdir} not found, exiting"
            cd $startdir
            exit
    fi

    # copy files to this directory
    cp $transitfile .
    cp -r $ttweeterdir .

    # build the image
    echo "building"
    docker build -t twtest .

    # clean up
    rm $tfname
    rm -r "./${tdirname}"
    echo "done"

    cd $dockerdir
}

function build_flaskContainer
{
    cd $dockerdir
    echo "building flaskContainer"
    container_dir="flaskContainer"

    # check directory exists
    if [ ! -d ${container_dir} ]
        then 
            echo "Error, ${dockerdir}/${container_dir} directory does not exist"
            cd $startdir
            exit
    fi

    # copy flask directory 

    cd $container_dir
    pwd

    flaskdir="flask"
    flasksrc="${rootdir}/${flaskdir}"
    if [ ! -d $flasksrc ]
        then
            echo "error, directory ${flasksrc} not found, exiting"
            cd $startdir
            exit
    fi

    # copy flask dir into container directory
    cp -r $flasksrc .

    # build container
    echo "building..."
    docker build -t flasktest .

    # clean up
    rm -r ${flaskdir}
    echo done

    cd $dockerdir

}

build_streamContainer
build_flaskContainer

cd $startdir


