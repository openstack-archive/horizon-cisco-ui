#!/bin/sh

# Many of horizon's repos suffer from the problem of depending on horizon,
# but it not existing on pypi.

# This wrapper for tox's package installer will use the existing package
# if it exists, else use zuul-cloner if that program exists, else grab it
# from horizon master via a hard-coded URL. That last case should only
# happen with devs running unit tests locally.

# From the tox.ini config page:
# install_command=ARGV
# default:
# pip install {opts} {packages}

ZUUL_CLONER=/usr/zuul-env/bin/zuul-cloner
horizon_installed=$(echo "import horizon" | python 2>/dev/null ; echo $?)

set -ex

cwd=$(/bin/pwd)

if [ $horizon_installed -eq 0 ]; then
    echo "ALREADY INSTALLED" > /tmp/tox_install.txt
    echo "Horizon already installed; using existing package"
elif [ -x "$ZUUL_CLONER" ]; then
    echo "ZUUL CLONER" > /tmp/tox_install.txt
    cd /tmp
    $ZUUL_CLONER --cache-dir \
        /opt/git \
        git://git.openstack.org \
        openstack/horizon
    cd openstack/horizon
    #$cwd/tools/add_horizon_patches.sh /tmp/openstack/horizon $cwd
    pip install -e .
    cd "$cwd"
else
    echo "PIP HARDCODE" > /tmp/tox_install.txt
    pip install -U -egit+https://git.openstack.org/openstack/horizon#egg=horizon
    #$cwd/tools/add_horizon_patches.sh $VIRTUAL_ENV/src/horizon $cwd
    pip install -U -e $VIRTUAL_ENV/src/horizon
fi

pip install -U $*
exit $?
