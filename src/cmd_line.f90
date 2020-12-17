module cmd_line
  implicit none
  integer, parameter :: MAX_NAMES_PER_ARG = 10
  integer, parameter :: MAX_ARG_NAME_LEN = 20
contains
  integer function get_arg_ind(names) result(ind)
    implicit none
    character, intent(in) :: names
    character(MAX_ARG_NAME_LEN) :: names_arr(MAX_NAMES_PER_ARG)

    read(names, *) names_arr
    print *,names
  end function get_arg_ind
end module cmd_line
