<!--
This is a Markdown file and is best viewed with a suitable program such as Okular.
These comments should not be visible when viewing this file with a proper program.
-->

Building the Fortran part of this project requires a Fortran compiler such as
[gfortran](https://gcc.gnu.org/wiki/GFortran).

Building the Python part of this project requires
Python 3 (tested with Python 3.9) and some packages from
[PyPI](https://pypi.org/).
The recommended way to install these packages is by using
[pip](https://pip.pypa.io/en/stable/) in a
[virtualenv](https://docs.python.org/3/library/venv.html).
You can create a virtualenv to the current folder by running
```python3 -m venv venv```.
Then you can activate it with
```source ./venv/bin/activate```
on Linux and by running the corresponding PowerShell script on Windows.
Now both the commands `python` and `python3` should point to the Python 3
installation of the virtualenv in the current shell session.
When the virtualenv has been set up, the packages can be installed by running
```pip install -r requirements.txt``` when in the src folder.
Alternatively you can use an IDE such as
[PyCharm](https://www.jetbrains.com/pycharm/), which will take care of the virtualenv and libraries for you.
However, since the requirements.txt is not at the root of this project, you may have to set its location
manually in the settings at
Tools &rarr; Python Integrated Tools &rarr; Packaging &rarr; Package requirements file.

When the all the dependencies have been installed, the project can be built by running ```make all```.
(Personally I would prefer to use a bash script instead, but the use of ```make``` is said to give bonus points.)
The
[GitHub Actions](https://github.com/features/actions)
[workflow files](../.github/workflows)
can be used as an additional template on how to build the project.

There are also precompiled binaries are available on
[GitHub](https://github.com/AgenttiX/planetary-motion/actions), but running the Python code requires the
installation of the necessary libraries regardless.

<!-- By the way, in my opinion it would be the best to put both build and usage
documentation in one README file in the root of the repository, since
this is a rather small project. -->
