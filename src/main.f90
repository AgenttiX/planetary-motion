! Please note that more features are available in the Python version

program main
  ! use cmd_line
  use utils
  implicit none

  character(:), allocatable :: path
  real(kind=REAL_KIND), allocatable :: m(:), x(:, :), v(:, :)
  real(kind=REAL_KIND) :: dt
  integer :: n_steps, n_objs, print_interval

  path = get_path()
  print *, "Using configuration file: ", path
  call read_file(path, x, v, m, dt, n_steps, n_objs, print_interval)
  print *, "n_objs: ", n_objs
  print *, "n_steps: ", n_steps
  print *, "dt: ", dt
  print *, "print_interval: ", print_interval
  call print_arr_2d(x, "x")
  call print_arr_2d(v, "v")
  call print_arr_1d(m, "m")

end program main
