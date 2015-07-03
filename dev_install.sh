#!/bin/sh

# Small script for installing Horizon plugins
# Defaults to Horizon IS installed at opt/stack/horizon

### Variables

# Change these for your specific plugin
ENABLED_FILE="_40_router.py" # Relative path

# These are defaults, may be useful to change but can normally be left alone
HORIZON_DIR="/opt/stack/horizon"

### Functions

function setup_horizon {
  echo "Is Horizon installed? [Y/n] ?"

  read INSTALLED
  
  case $INSTALLED in
    [yY]|"")
      set_directory
      ;;
    [nN])
      STACK_DIR="/opt/stack"
      echo "Checking for presence of $STACK_DIR..."
      if [ ! -d "$STACK_DIR" ] ; then
        echo "$STACK_DIR not found. Creating (requires sudo)..."
        sudo mkdir -p $STACK_DIR
        sudo chown -R $USER $STACK_DIR
        chmod 0755 $STACK_DIR
      fi

      echo "Checking for git..."
      if command -v git >/dev/null 2>&1 ; then
        git clone https://github.com/openstack/horizon.git /opt/stack/horizon
      else
        echo "Git is not available, but is required. Please install git."
        exit 1
      fi
      ;;
    *)
      echo "Input not recognised"
      setup_horizon
      ;;
  esac
}

function set_directory {
  echo "Please enter your Horizon root directory. Leave blank for default [$HORIZON_DIR]:"

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
}

function copy_enabled_file {
  ENABLED_DIR=$HORIZON_DIR"/openstack_dashboard/enabled/"

  if [ -d "$ENABLED_DIR" ] ; then
    echo "\nCopying $ENABLED_FILE to $ENABLED_DIR..."
    if [ -f $ENABLED_DIR$ENABLED_FILE ] ; then
      rm "$ENABLED_DIR$ENABLED_FILE"
    else
      if cp $ENABLED_FILE $ENABLED_DIR ; then
        echo "Copy succeeded"
      else
        echo "Copy failed"
        exit 1
      fi
    fi
  fi
}

function install_plugin {
  echo "\nChecking for existing venv..." 
  if [ ! -d $HORIZON_DIR"/.venv" ] ; then
    echo "No venv found"
    python $HORIZON_DIR"/tools/install_venv.py"
  else
    echo "Existing venv found [$HORIZON_DIR/.venv]"
  fi

  echo "\nInstalling plugin..."
  if $HORIZON_DIR/tools/with_venv.sh pip install -e . ; then
    echo "Plugin installed"
  else
    echo "Plugin installation failed"
    exit 1
  fi
}

function launch_horizon {
  cd $HORIZON_DIR

  echo "\nChecking for settings file..."
  if [ -f openstack_dashboard/local/local_settings.py ] ; then
    echo "Settings file found [$PWD/openstack_dashboard/local/local_settings.py]"
  else
    echo "Settings file not found. Using default..."
    cp openstack_dashboard/local/local_settings.py.example openstack_dashboard/local/local_settings.py
  fi

  echo "\nLaunching Horizon at 127.0.0.1:8080..."
  ./run_tests.sh --runserver 127.0.0.1:8080
}

### Execution

setup_horizon
install_plugin
copy_enabled_file
launch_horizon
