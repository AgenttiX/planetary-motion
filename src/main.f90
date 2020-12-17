! Please note that more features are available in the Python version



program main
  use cmd_line
  implicit none
  integer :: i
  print *, "Hello World!"
  i = get_arg_ind("asdf,foo")
end program main
