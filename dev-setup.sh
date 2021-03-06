#! /bin/bash

PYTHON_VERSION=2.7
if [[ "X$1" != "X" ]]; then
  PYTHON_VERSION=$1
fi


OLDPWD=$(pwd)

SOURCE=${BASH_SOURCE[0]}

if [[ "XX$SOURCE" = "XX" ]]; then
    SOURCE=$0
fi

DIR=$( cd "$( dirname "$SOURCE" )" && pwd )
VENV_DIR=$DIR/venv
cd "$DIR"


function missing() {
    hash $1 2>/dev/null
    if [[ $? -eq 1 ]]; then
        # Apparently 0 is true.
        return 0
    else
        return 1
    fi
}

function install() {
    # `pip show` outputs nothing if the package is not installed.
    if ! pip freeze | grep -iq "$1"; then
        echo "Installing $1"
        pip install $1
    fi
}

if missing pip; then
    echo "Please install pip before running this."
    return
fi

if [[ $VIRUTAL_ENV != $DIR* ]]; then
    install virtualenv

    if [ ! -d "$VENV_DIR" ]; then
        # Create a new environment.
        virtualenv --system-site-packages -p `which python$PYTHON_VERSION` $VENV_DIR
        # And configure it to use python 2.7
    fi

    # Activate if not already active.
    source $VENV_DIR/bin/activate >/dev/null 2>&1
fi


pip install -q --upgrade -r dev-requirements.txt

python -c "import pcapy" > /dev/null 2>&1

if [[ $? -eq 1 ]]; then
  if [[ `which apt-get` ]]; then
    sudo apt-get install -q python-pcapy
  else
    echo "Please install pcapy some other way."
    # pip install -q -e git://github.com/CoreSecurity/pcapy.git@0.10.8#egg=pcapy-master
  fi
fi

# Return to old directory.
cd $OLDPWD

echo "Virtual Environment all configured."
# echo " If this was run using source; then everything is ready."
# echo ""
# echo "      source $0"
# echo ""
echo "To deactivate run"
echo ""
echo "      deactivate"
echo ""
