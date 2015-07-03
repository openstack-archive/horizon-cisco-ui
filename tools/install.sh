#!/bin/sh

# Variables

HORIZON_DIR="/opt/stack/horizon/"
ENABLED_FILE="_40_router.py"

# Functions

function set_directory {
  echo "Please enter your Horizon root directory. Leave blank for default ($HORIZON_DIR):"

  read CUSTOM_DIR

  if [ ! -z "${CUSTOM_DIR// }" ]  ; then
    if [[ $CUSTOM_DIR == /*/ ]] ; then
      HORIZON_DIR=$CUSTOM_DIR
    elif [[ $CUSTOM_DIR == */ ]] ; then
      HORIZON_DIR=/$CUSTOM_DIR
    elif [[ $CUSTOM_DIR == /* ]] ; then
      HORIZON_DIR=$CUSTOM_DIR/
    else
      HORIZON_DIR=/$CUSTOM_DIR/
    fi
  fi

  echo "Horizon directory is $HORIZON_DIR"
}

function copy_enabled_file {
  ENABLED_DIR=$HORIZON_DIR"openstack_dashboard/enabled/"

  if [ -d "$ENABLED_DIR" ] ; then
    echo "\nCopying $ENABLED_FILE ..."
    if cp $ENABLED_FILE $ENABLED_DIR ; then
      echo "Copy succeeded"
    else
      echo "Copy failed"
    fi
  fi
}

# Execution

set_directory
copy_enabled_file
