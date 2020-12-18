! If this weren't a course project, I would have used Python or some existing Fortran library for the
! command line argument parsing, as Fortran isn't designed for these kind of things.
! http://fortranwiki.org/fortran/show/Command-line+arguments

module cmd_line
  implicit none
  integer, parameter :: MAX_ARG_NAME_LEN = 20
contains
  integer function get_arg_ind(names) result(ind)
    implicit none
    ! The * means that the length of the string is determined by the caller
    character(*), intent(in) :: names

    character(len=MAX_ARG_NAME_LEN), allocatable :: names_arr(:)
    character(len=MAX_ARG_NAME_LEN) :: asdf
    integer :: i, num_names, num_args, ios
    ios = 0
    num_args = command_argument_count()
    num_names = -1

    do while (ios == 0)
      num_names = num_names + 1
      read(names, *, iostat=ios) asdf
      print *,asdf, num_names
    end do
    print *, "num_names", num_names

!    do i=1,size(names_arr)
!      names_arr(i) = ""
!    end do

    read(names, *) names_arr
    print *,names
  end function get_arg_ind
end module cmd_line
