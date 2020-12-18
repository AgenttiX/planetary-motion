! Please note that more features are available in the Python version

program main
  ! use cmd_line
  use utils
  implicit none

  character(:), allocatable :: path
  real(kind=REAL_KIND), allocatable :: m(:), x(:, :), v(:, :)
  real(kind=REAL_KIND) :: dt
  integer :: n_steps, n_objs

  path = get_path()
  print *, path
  call read_file(path, x, v, m, dt, n_steps, n_objs)

end program main
