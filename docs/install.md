# Dependencies

    sudo apt-get install python3 python3-pip build-essential
    sudo apt-get build-dep python3-lxml

# Virtualenv (optional)

Use a Python virtual environment if you have other Python projects, whose dependencies might conflict with LQMToolset (or vice-versa). `virtualenv` ensures that Python projects are isolated.

    sudo pip3 install virtualenv
    virtualenv -p `which python3` lqmt
    source lqmt/bin/activate

# LQMToolset

    pip3 install lqmt
