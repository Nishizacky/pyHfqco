# /bin/bash

pip install --upgrade pip
pip install cmake
git clone "https://github.com/JoeyDelp/JoSIM"
cd JoSIM && mkdir build && cd build
cmake ..
cmake --build . --config Release
make install