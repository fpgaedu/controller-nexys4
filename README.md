# fpgaedu-nexys4-python
Fpgaedu Board component source generation package for Digilent Nexys 4. HDL sources are defined through MyHDL python package. 

## Installation
First, get this project's sources:
```
git clone https://github.com/matthijsbos/fpgaedu-nexys4-python.git
```
Then, navigate into the project folder and run the installation script:
```
cd fpgaedu-nexys4-python
python setup.py install
```
## Execution
To execute the source code generation script, execute:
```
python -m fpgaedu.hdl.nexys4.generate_vhdl -o OUTPUTDIR -a ADDRESSWIDTH -d DATAWIDTH -t TOPLEVEL -r RESETACTIVE
```
In order to get argument help, execute:
```
python -m fpgaedu.hdl.nexys4.generate_vhdl --help
```

## Development installation
For development environment setup, a virtualenv is recommended. 
```
virtualenv virtualenv-fpgaedu
source virtualenv-fpgaedu/bin/activate
```
Then, install the sources in development mode:
```
git clone https://github.com/matthijsbos/fpgaedu-nexys4-python.git
cd fpgaedu-nexys4-python
python setup.py develop
```
