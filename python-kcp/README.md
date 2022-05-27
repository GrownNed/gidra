Python-Kcp
=========
    Python binding for KCP, 
    what is KCP? please visit: https://github.com/skywind3000/kcp, 
    http://www.skywind.me/blog/archives/1048

Wiki
----
    基于Cython实现KCP源码的python封装

前置库
-----
    1.Python2.x / Python3.x

    2.python-pip         #sudo apt-get install python-pip python-dev build-essential
                         #sudo pip install --upgrade pip
    
    3.Cython             #sudo pip install Cython
    
    4.python-setuptools  #sudo apt-get install python-setuptools

支持平台
-----
    Linux(Ubuntu)

安装库
-----
    sudo sh setup.sh / sudo sh setup.sh $YOUR_PYTHON_PATH

运行测试程序
-----
    python test/testkcp.py