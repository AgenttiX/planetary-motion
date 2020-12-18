! If this weren't a course project with the implicit requirement of doing everything ourselves,
! I would have used Python or some existing Fortran library for the
! command line argument parsing, as Fortran isn't designed for these kind of things.
! http://fortranwiki.org/fortran/show/Command-line+arguments

module cmd_line
  implicit none
  integer, parameter :: MAX_ARG_LEN = 200
contains
  integer function get_arg_ind(names) result(ind)
    ! NOTE
    ! It turned out that this method wasn't needed after all, so it's incomplete
    ! (At first I thought that the timestep arguments were supposed to be read from the command line)

    ! Return codes:
    ! > 0 = position
    ! 0 = should not happen (not used since in many other languages 0 means OK and arrays also begin from 0)
    ! -1 = not found
    ! -2 = found multiple
    ! -3 = misc error
    implicit none
    ! The * means that the length of the strings is determined by the caller
    character(*), intent(in) :: names(:)

    character(len=MAX_ARG_LEN) :: text
    integer :: i, j, num_names, num_args, ios
    ind = 0
    ios = 0
    num_args = command_argument_count()
    num_names = -1

    do i=1, size(names)
      do j=1, num_args
        call get_command_argument(j, text, status=ios)
        if (ios /= 0) then
          ind = -3
          return
        end if
      end do
    end do

  end function get_arg_ind
end module cmd_line
