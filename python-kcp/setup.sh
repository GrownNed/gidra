PYTHON=python
if [ $# -ge 1 ]; then
	PYTHON=$1
fi
pip install -r requirements.txt
$PYTHON setup.py build
$PYTHON setup.py install
rm -rf build dist lkcp.egg-info
PY_VERSION=`$PYTHON -V 2>&1|awk '{print $2}'|awk -F '.' '{print $1"."$2"."$3}'`
echo 'install python version:' $PY_VERSION
