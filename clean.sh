set -x
rm -rf ./gen_data.egg-info
find -type f -name \*pyc -exec rm {} \;
find -type d -name __pycache__ -exec rm -rf {} \;
