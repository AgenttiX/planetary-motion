! If this weren't a course project with the implicit requirement of doing everything ourselves,
! I would have used Python or some existing Fortran library for the
! file parsing, as Fortran isn't designed for these kind of things.
! https://github.com/jacobwilliams/json-fortran
! https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_csv.html
! https://www.geeksforgeeks.org/read-a-file-line-by-line-in-python/

module utils
  integer, parameter :: DIMS = 3
  integer, parameter :: FILE_UNIT = 10
  integer, parameter :: MAX_LINE_LEN = 100
  integer, parameter :: REAL_KIND = 8
  character(len=*), parameter :: DEFAULT_PATH = "../run/config.txt"
contains
  integer function bool2int(val)
    logical, intent(in) :: val
    if (val) then
      bool2int = 1
    else
      bool2int = 0
    end if
  end function bool2int

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
    real(kind=REAL_KIND), intent(in) :: arr(:)
    character(len=*), intent(in), optional :: name

    integer :: i

    if(present(name)) then
      print *, name
    end if
    do i=1, size(arr)
      print *, arr(i)
    end do
  end subroutine print_arr_1d

  subroutine print_arr_2d(arr, name)
    implicit none
    real(kind=REAL_KIND), intent(in) :: arr(:, :)
    character(len=*), intent(in), optional :: name

    integer :: arr_shape(2)
    integer :: i
    arr_shape = shape(arr)

    if(present(name)) then
      print *, name
    end if
    do i=1, arr_shape(2)
      print *, arr(:, i)
    end do
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

  ! File processing methods

  integer function get_num_lines(path) result(n)
    ! Based on
    ! https://stackoverflow.com/questions/30692424/how-to-read-number-of-lines-in-fortran-90-from-a-text-file
    ! Return codes:
    ! > 0 = number of lines
    ! -1 = could not open file
    ! -2 = could not read a line in the file
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
      read(FILE_UNIT, *, iostat=ios)
      if (ios > 0) then
        n = -2
        return
      else if (ios < 0) then
        exit
      end if
      n = n + 1
    end do
    close(FILE_UNIT)
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

  subroutine read_file(path, x, v, m, dt, n_steps, n_objs, print_interval)
    implicit none
    character(len=*), intent(in) :: path
    integer, intent(out) :: n_objs, n_steps, print_interval
    real(kind=REAL_KIND), allocatable, intent(out) :: m(:), x(:, :), v(:, :)
    real(kind=REAL_KIND), intent(out) :: dt

    real(kind=REAL_KIND) :: t
    character(len=MAX_LINE_LEN) line, trimmed, name, value, current_array
    integer :: ios, i_line, arrays_started, scalars_started, delim_pos, arrays_allocated, array_index

    open(unit=FILE_UNIT, file=path, status="old", iostat=ios)
    if (ios /= 0) then
      print *, "Opening the file failed"
      stop
    end if

    ! Header check
    read(FILE_UNIT, "(a)", iostat=ios) line
    if (ios /= 0 .or. line /= "planetary-motion configuration") then
      print *, "Invalid header in file: ", path
      stop
    end if

    ! Actual reading
    t = -1
    dt = -1
    n_objs = -1
    n_steps = -1
    print_interval = 0

    i_line = 0
    scalars_started = 0
    arrays_started = 0
    arrays_allocated = 0
    current_array = ""
    array_index = 0
    do
      i_line = i_line + 1
      read(FILE_UNIT, "(a)", iostat=ios) line
      ! Check for errors and end of file
      if (ios > 0) then
        print *,"Could not read line ", i_line
      else if (ios < 0) then
        exit
      end if
      ! Skip comments and empty lines
      ! Note that trimming an empty line does not result in a string of length 0,
      ! but an empty string does equal " "
      trimmed = trim(line)
      if(trimmed == " " .or. trimmed(1:1) == "#" .or. trimmed(1:1) == ";") then
        cycle
      end if

      ! Process the line contents
      if (trimmed == "[scalars]") then
        if (arrays_started == 1) then
          print *,"Cannot start scalars twice"
          stop
        end if
        scalars_started = 1
        arrays_started = 0
      else if (trimmed == "[arrays]") then
        if (arrays_started == 1) then
          print *,"Cannot start arrays twice"
          stop
        end if
        arrays_started = 1
        scalars_started = 0
      ! Scalar processing
      else if (scalars_started == 1) then
        delim_pos = scan(trimmed, "=")
        if(delim_pos < 1) then
          print *, "Could not parse delimiter on scalar configuration line: ", line
          stop
        end if
        name = trim(trimmed(1:delim_pos-1))
        value = trim(trimmed(delim_pos+1:))
        if (name == "n_objs") then
          read(value, *, iostat=ios) n_objs
        else if (name == "n_steps") then
          read(value, *, iostat=ios) n_steps
        else if (name == "dt") then
          read(value, *, iostat=ios) dt
        else if (name == "t") then
          read(value, *, iostat=ios) t
        end if
        if (ios /= 0) then
          print *, "Could not convert value to correct type on configuration line: ", line
        end if
      ! Array processing
      else if (arrays_started == 1) then
        ! Allocate memory if not yet allocated
        if (n_objs < 1) then
          print *, "n_objs must be specified before starting arrays for proper memory allocation"
          stop
        else if (arrays_allocated == 0) then
          allocate(x(DIMS, n_objs), v(DIMS, n_objs), m(n_objs))
          arrays_allocated = 1
        end if

        if (current_array == " ") then
          current_array = trimmed
          array_index = 0
          ! print *, "processing array ", current_array
        else
          array_index = array_index + 1

          if (current_array == "x") then
            read(trimmed, *, iostat=ios) x(:, array_index)
          else if (current_array == "v") then
            read(trimmed, *, iostat=ios) v(:, array_index)
          else if (current_array == "m") then
            read(trimmed, *, iostat=ios) m(array_index)
          end if
          if (ios /= 0) then
            print *, "Could not put the line '", line, "' into array ", current_array
          end if

          if (array_index == n_objs) then
            current_array = ""
          end if
        end if
      end if
    end do
    close(FILE_UNIT)

    ! Post-processing and checks
    if (bool2int(dt > 0) + bool2int(t > 0) + bool2int(n_steps > 0) /= 2) then
      print *, "Exactly two of td, t and n_steps must be configured"
      stop
    end if
    if (dt < 0) then
      dt = t / n_steps
    else if (n_steps < 0) then
      n_steps = nint(t / dt)
    end if

  end subroutine read_file
end module utils
