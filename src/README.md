<!-- This is a Markdown file and is best viewed with a suitable program such as Okular -->

Building the Fortran part of this project requires a Fortran compiler such as
[gfortran](https://gcc.gnu.org/wiki/GFortran).

Building the Python part of this project requires
Python 3 (tested with Python 3.8) and some packages from
[PyPI](https://pypi.org/).
The recommended way to install these packages is by using
[pip](https://pip.pypa.io/en/stable/) in a
[virtualenv](https://docs.python.org/3/library/venv.html).
When the virtualenv has been set up, the packages can be installed with
`pip install -r requirements.txt` when in the src folder.

When the all the dependencies have been installed, the project can be built by running the
[build script](build.sh).

The
[GitHub Actions](https://github.com/features/actions)
[workflow files](../.github/workflows)
can be used as an additional template on how to build the project.

<!-- By the way, in my opinion it would be the best to put both build and usage
documentation in one README file in the root of the repository, since
this is a rather small project. -->
