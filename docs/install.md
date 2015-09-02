# Install

### Dependencies

    sudo apt-get install python3 python3-pip
    sudo apt-get build-dep python3-lxml


### Virtualenv (optional)

Use a Python virtual environment if you have other Python projects, whose dependencies might conflict with LQMToolset (or vice-versa). `virtualenv` ensures that Python projects are isolated.

    sudo apt-get install python3-virtualenv
    virtualenv -p `which python3` lqmt
    cd lqmt/
    source bin/activate


### LQMToolset

    pip3 install lqmt
