! If this weren't a course project with the implicit requirement of doing everything ourselves,
! I would have used Python or some existing Fortran library for the
! file parsing, as Fortran isn't designed for these kind of things.
! https://github.com/jacobwilliams/json-fortran
! https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_csv.html
! https://www.geeksforgeeks.org/read-a-file-line-by-line-in-python/

module utils
  integer, parameter :: FILE_UNIT = 10
  integer, parameter :: MAX_LINE_LEN = 100
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

  subroutine print_arr_1d(arr, name)
    implicit none
    real(kind=REAL_KIND), intent(in) :: arr(:, :)
    character(len=*), intent(in), optional :: name
    if(present(name)) then
      print *, name
    end if
    print *, arr
  end subroutine print_arr_1d

  subroutine print_arr_2d(arr, name)
    implicit none
    real(kind=REAL_KIND), intent(in) :: arr(:, :)
    character(len=*), intent(in), optional :: name
    if(present(name)) then
      print *, name
    end if
    print *, arr
  end subroutine

!  integer function find_line_number(unit, search_str) result(line_num)
!    implicit none
!    integer, intent(in) :: unit
!    character(len=*), intent(in) :: search_str
!
!    character(len=MAX_LINE_LEN) :: line
!    character(len=MAX_LINE_LEN) :: word
!    integer :: ios
!    line_num = -1
!    do
!      read(unit, "(a)", iostat=ios) line
!      if (ios /= 0) exit
!      read (text, *) word
!      if (word == search_str) then
!        line_num =
!      end if
!    end do
!  end function find_line_number

  integer function get_num_lines(path) result(n)
    ! Based on
    ! https://stackoverflow.com/questions/30692424/how-to-read-number-of-lines-in-fortran-90-from-a-text-file
    implicit none
    character(len=*), intent(in) :: path
    integer :: ios
    n = 0
    open(unit=FILE_UNIT, file=path, status="old", iostat=ios)
    if (ios /= 0) then
      n = -1
      return
    end if
    do
      read(FILE_UNIT, *, end=10)
      n = n + 1
    end do
    10 close(FILE_UNIT)
  end function get_num_lines

  integer function read_file_to_arr(path, file) result(ret)
    implicit none
    character(len=*), intent(in) :: path
    character(len=MAX_LINE_LEN), intent(out), allocatable :: file(:)
    integer :: n_lines, i, ios

    n_lines = get_num_lines(path)
    if (n_lines < 0) then
      ret = -1
      return
    end if
    allocate(file(1:n_lines))
    open(unit=FILE_UNIT, file=path, status="old", iostat=ios)
    do i=1, n_lines
      read(FILE_UNIT, *, iostat=ios) file(i)
      if(ios /= 0) then
        ret = -1
        return
      end if
    end do
    close(FILE_UNIT)
  end function read_file_to_arr

!  function read_arg_real(unit, name) result(arg)
!    implicit none
!    integer, intent(in) :: unit
!
!  end function read_arg_real
!
!  function read_arg_int(unit, name) result(arg)
!
!  end function read_arg_int

  subroutine read_file(path, x, v, m, dt, n_steps, n_objs)
    implicit none
    character(len=*), intent(in) :: path
    integer, intent(out) :: n_objs, n_steps
    real(kind=REAL_KIND), allocatable, intent(out) :: m(:), x(:, :), v(:, :)
    real(kind=REAL_KIND), intent(out) :: dt

    character(len=MAX_LINE_LEN) line
    integer :: ios, n_lines
    n_lines = get_num_lines(path)
    if (n_lines < 0) then
      print *, "Could not open config file :", path
      stop
    end if

    open(unit=FILE_UNIT, file=path, status="old", iostat=ios)
    if (ios /= 0) then
      print *, "Opening the file failed"
      stop
    end if

    read(FILE_UNIT, "(a)", iostat=ios) line
    if (ios /= 0 .or. line /= "planetary-motion configuration") then
      print *, "Invalid header in file: ", path
      stop
    end if

    read(FILE_UNIT, "(a)", iostat=ios) line
    if (ios /= 0 .or. line /= "n_objs") then

    end if

    close(FILE_UNIT)
  end subroutine read_file
end module utils
