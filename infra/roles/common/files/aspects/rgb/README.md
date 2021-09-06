# RGB

## Copy

rsync -avzhC ~/workspace/rgb/ dietpi@cyan:/home/dietpi/rgb

## Invoke

sudo docker run -p 54321:54321 --privileged rgb

# https://packaging.python.org/tutorials/packaging-projects/

# Install scipy
https://stackoverflow.com/a/66536896


pip3 install cython pybind11
pip3 install --no-binary :all: --no-use-pep517 numpy

brew install openblas gfortran
export OPENBLAS=/opt/homebrew/opt/openblas/lib/

pip install pythran
pip3 install --no-binary :all: --no-use-pep517 scipy