import subprocess

import numpy as np

# Compilation is done automatically here to speed up development
print("Compiling Fortran code")
subprocess.run(["./build.sh"], check=True)
print("\n\n")

# This line may show errors in an IDE, since the generated Python module is found dynamically
import core


def main():
    n_objs = 10
    dt = 0.1
    n_iters = 10

    x = np.asfortranarray(np.random.rand(3, n_objs))
    v = np.zeros_like(x)
    a = np.zeros_like(x)
    m = np.ones(n_objs, order="F")

    core.iterate(x, v, a, m, dt, n_iters)

    print("x")
    print(x)
    print("v")
    print(v)
    print("a")
    print(a)


if __name__ == "__main__":
    main()
