# Dependencies

LQMT is written completely in Python3. Because of this, Python3 is required to install and run LQMT properly. These instructions should get you setup with Python3. Note that if your system already has Python3, you should only have to use the instructions below to install lxml.

##### Debian/Ubuntu

    sudo apt-get install python3 python3-pip build-essential
    sudo apt-get build-dep python3-lxml

##### RedHat/CentOS 6

    sudo yum install https://dl.iuscommunity.org/pub/ius/stable/Redhat/6/x86_64/ius-release-1.0-14.ius.el6.noarch.rpm
    sudo yum install python34u python34u-pip libxml2-devel libxslt-devel python34u-devel gcc

##### RedHat/CentOS 7

    sudo yum install https://dl.iuscommunity.org/pub/ius/stable/Redhat/7/x86_64/ius-release-1.0-14.ius.el7.noarch.rpm
    sudo yum install python34u python34u-pip libxml2-devel libxslt-devel python34u-devel gcc

##### FreeBSD
    pkg install python34
    wget https://bootstrap.pypa.io/get-pip.py
    python3.4 get-pip.py
    pkg install py34-sqlite3
    pkg install py27-lxml

# Virtualenv (optional)

Use a Python virtual environment if you have other Python projects, whose dependencies might conflict with LQMToolset (or vice-versa). `virtualenv` ensures that Python projects are isolated.

    sudo pip3 install virtualenv
    virtualenv -p `which python3` lqmt
    source lqmt/bin/activate

# LQMToolset

    pip3 install lqmt
    lqmt -h

If you successfully ran lqmt with the help command, you can move on to configuration. 
