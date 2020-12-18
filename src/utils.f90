module utils
  integer, parameter :: REAL_KIND = 8
  character(len=*), parameter :: DEFAULT_PATH = "../run/config.txt"
contains
  function get_path() result(path)
    implicit none
    integer :: ios, num_args
    character(:), allocatable :: path

    num_args = command_argument_count()
    if (num_args < 0) then
      print *, "Error when querying number of command line arguments"
      stop
    else if (num_args > 1) then
      print *,"Too many arguments"
      stop
    else if (num_args == 1) then
      call get_command_argument(1, path, status=ios)
      if (ios /= 0) then
        print *, "Error when fetching command line argument"
        stop
      end if
    else
      path = DEFAULT_PATH
    end if
  end function get_path

  subroutine read_file(path, x, v, m, dt, n_steps, n_objs)
    implicit none
    character(len=*), intent(in) :: path
    integer, intent(out) :: n_objs, n_steps
    real(kind=REAL_KIND), allocatable, intent(out) :: m(:), x(:, :), v(:, :)
    real(kind=REAL_KIND), intent(out) :: dt

    integer :: ios

    open(unit=10, file=path, status="old", iostat=ios)
    if (ios /= 0) then
      print *, "Opening the file failed"
      stop
    end if

    close(10)
  end subroutine read_file
end module utils
