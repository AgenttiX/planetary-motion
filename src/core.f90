module core
  ! Apparently the use of module constants is broken in F2PY despite the use of F2PY specific type declarations.
  ! With those declarations the Python module compiles but segfaults when loaded.
  ! https://stackoverflow.com/questions/19983850/f2py-access-module-parameter-from-subroutine
  ! Therefore these constants have been re-declared in the functions.
  ! With more time this issue could be debugged further.

  implicit none
!  integer, parameter :: DIMS = 3
!  integer, parameter :: REAL_KIND = 8
!  real(kind=REAL_KIND), parameter :: G = 1
!  real(kind=REAL_KIND), parameter :: MIN_DIST = 0.01
!
!  integer, parameter :: OUTPUT_FILE_UNIT = 11
!  integer, parameter :: MAX_PATH_LEN = 200
!  character(len=*), parameter :: DEFAULT_OUTPUT_PATH = "../run/output"
contains
  function force(x, m, i, n_objs, g, min_dist)
    implicit none

    ! For some reason replacing these with the f2py variable declarations
    ! does not work like it does in the other functions
    integer, parameter :: DIMS = 3
    integer, parameter :: REAL_KIND = 8
    ! real(kind=REAL_KIND), parameter :: G = 1
    ! real(kind=REAL_KIND), parameter :: MIN_DIST = 0.01

    integer, intent(in) :: i, n_objs
    real(kind=REAL_KIND), intent(in) :: x(DIMS,n_objs), m(n_objs), g, min_dist

    real(kind=REAL_KIND) :: force(DIMS), dist
    integer :: j
    force = 0

    do j=1,n_objs
      dist = sqrt(sum((x(:,i) - x(:,j))**2))
      ! Clipping prevents overflow
      if (dist > min_dist) then
        force = force + g*m(i)*m(j)*(x(:,j) - x(:,i)) / dist**3
      end if
    end do
  end function force

  subroutine iterate(x, v, a, m, dt, n_steps, n_objs, g, min_dist, print_interval, write_interval, path)
    ! Note that on Python side the argument n_objs is optional, since it can be automatically determined from the input arrays
    implicit none

    integer, parameter :: DIMS = 3
    integer, parameter :: REAL_KIND = 8
    integer, parameter :: MAX_PATH_LEN = 200
    character(len=*), parameter :: DEFAULT_OUTPUT_PATH = "../run/output"

    ! Double precision is used for NumPy compatibility and more accurate results
    integer, intent(in) :: n_steps, n_objs
    integer, intent(in), optional :: print_interval, write_interval
    character(len=*), intent(in), optional :: path
    real(kind=REAL_KIND), intent(inout) :: x(DIMS,n_objs), v(DIMS,n_objs), a(DIMS,n_objs)
    real(kind=REAL_KIND), intent(in) :: m(n_objs), dt, g, min_dist

    integer :: i, iter, print_interval_checked, write_interval_checked, written
    character(len=MAX_PATH_LEN) :: path_checked
    real(kind=REAL_KIND) :: a_prev(DIMS)
    written = 0

    ! Processing of optional arguments
    if(present(print_interval)) then
      print_interval_checked = print_interval
    else
      print_interval_checked = 0
    end if
    if(present(write_interval)) then
      write_interval_checked = write_interval
    else
      write_interval_checked = 0
    end if
    if(present(path)) then
      path_checked = path
    else
      path_checked = DEFAULT_OUTPUT_PATH
    end if

    ! Simulation loop
    do iter=1,n_steps
      x = x + v*dt + 0.5*a*dt**2
      do i=1,n_objs
        a_prev = a(:,i)
        a(:,i) = force(x, m, i, n_objs, g, min_dist) / m(i)
        v(:,i) = v(:,i) + 0.5*(a(:,i) + a_prev)*dt
      end do

      ! Writing and printing
      if (write_interval_checked /= 0 .and. mod(iter, write_interval_checked) == 0) then
        call write_progress(x, v, a, iter, n_objs, path)
        written = written + 1
      end if
      if (print_interval_checked /= 0 .and. mod(iter, print_interval_checked) == 0) then
        call print_progress(x, v, a, iter, dt, n_steps, n_objs)
      end if
    end do
  end subroutine iterate

  subroutine print_arr_1d(arr, name, unit)
    implicit none
    integer, parameter :: REAL_KIND = 8

    real(kind=REAL_KIND), intent(in) :: arr(:)
    character(len=*), intent(in), optional :: name
    integer, intent(in), optional :: unit

    integer :: i, unit_checked

    if (present(unit)) then
      unit_checked = unit
    else
      unit_checked = 6
    end if

    if(present(name)) then
      write(unit_checked, *) name
    end if

    do i=1, size(arr)
      write(unit_checked, *) arr(i)
    end do
  end subroutine print_arr_1d

  subroutine print_arr_2d(arr, name, unit)
    implicit none
    integer, parameter :: REAL_KIND = 8

    real(kind=REAL_KIND), intent(in) :: arr(:, :)
    character(len=*), intent(in), optional :: name
    integer, intent(in), optional :: unit

    integer :: arr_shape(2)
    integer :: i, unit_checked
    arr_shape = shape(arr)

    if (present(unit)) then
      unit_checked = unit
    else
      unit_checked = 6
    end if

    if(present(name)) then
      write(unit_checked, *) name
    end if

    do i=1, arr_shape(2)
      write(unit_checked, *) arr(:, i)
    end do

  end subroutine

  subroutine print_progress(x, v, a, i, dt, n_steps, n_objs)
    implicit none

    integer, parameter :: DIMS = 3
    integer, parameter :: REAL_KIND = 8

    integer, intent(in) :: i, n_steps, n_objs
    real(kind=REAL_KIND), intent(in) :: x(DIMS,n_objs), v(DIMS,n_objs), a(DIMS,n_objs)
    real(kind=REAL_KIND), intent(in) :: dt

    print *, "Iteration: ", i, "/", n_steps
    print *, "Time: ", i*dt
    print *, "Objects: ", n_objs
    call print_arr_2d(x, "x")
    call print_arr_2d(v, "v")
    call print_arr_2d(a, "a")
  end subroutine print_progress

  subroutine write_progress(x, v, a, i, n_objs, path)
    implicit none
    integer, parameter :: DIMS = 3
    integer, parameter :: REAL_KIND = 8
    integer, parameter :: OUTPUT_FILE_UNIT = 11
    integer, parameter :: MAX_PATH_LEN = 200

    integer, intent(in) :: i, n_objs
    real(kind=REAL_KIND), intent(in) :: x(DIMS,n_objs), v(DIMS,n_objs), a(DIMS,n_objs)
    character(len=*), intent(in) :: path

    integer :: ios
    character(len=MAX_PATH_LEN) :: full_path

    write(full_path, "(a,'/',I0.6,'.txt')", iostat=ios) trim(path), i
    if (ios /= 0) then
      print *,"Failed to create full path for output file: ", full_path
      stop
    end if
    open(OUTPUT_FILE_UNIT, file=full_path, iostat=ios, status="new", form="formatted")
    if (ios /= 0) then
      print *, "Failed to create output file to path: ", full_path
    end if
    call print_arr_2d(x, "x", OUTPUT_FILE_UNIT)
    call print_arr_2d(v, "v", OUTPUT_FILE_UNIT)
    call print_arr_2d(a, "a", OUTPUT_FILE_UNIT)

    close(OUTPUT_FILE_UNIT)
  end subroutine write_progress
end module core
