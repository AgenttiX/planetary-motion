! Please note that more features are available in the Python version

program main
  ! use cmd_line
  use core
  use utils
  implicit none

  character(len=MAX_PATH_LEN) :: config_path, output_path
  real(kind=REAL_KIND), allocatable :: m(:), x(:, :), v(:, :), a(:, :)
  real(kind=REAL_KIND) :: dt
  integer :: n_steps, n_objs, print_interval, write_interval, ios

  ! Argument processing
  call get_paths(config_path, output_path)

  ! Config processing
  print *, "Using configuration file: ", trim(config_path)
  print *, "Output will be written to: ", trim(output_path)
  call read_config(config_path, x, v, m, dt, n_steps, n_objs, print_interval, write_interval)
  print *, "n_objs: ", n_objs
  print *, "n_steps: ", n_steps
  print *, "dt: ", dt
  print *, "print_interval: ", print_interval
  print *, "write_interval: ", write_interval
  call print_arr_2d(x, "x")
  call print_arr_2d(v, "v")
  call print_arr_1d(m, "m")

  allocate(a(DIMS, n_objs))
  call system("mkdir -p " // trim(output_path), status=ios)
  if (ios /= 0) then
    print *, "Failed to create output directory"
    stop
  end if
  call system("rm -f " // trim(output_path) // "/*.txt", status=ios)
  if (ios /= 0) then
    print *, "Failed to clean output directory"
    stop
  end if

  print *, "Simulating"
  call iterate(x, v, a, m, dt, n_steps, n_objs, print_interval, write_interval, output_path)
end program main
