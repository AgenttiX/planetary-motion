subroutine iterate(x, v, a, m, dt, n_iters)
  implicit none
  real, intent(inout) :: x(:,:)
  real, intent(inout) :: v(:,:)
  real, intent(inout) :: a(:,:)
  real, intent(in) :: m(:)
  real, intent(in) :: dt
  integer, intent(in) :: n_iters

  integer :: i, iter
  integer :: dims(2)
  real :: a_prev(3)

  dims = shape(x)

  do iter=1,n_iters
    x = x + v*dt + 0.5*a*dt**2
    do i=1,dims(2)
      a_prev = a(:,i)
      ! a(:,i) = F()
      v(:,i) = v(:,i) + 0.5*(a(:,i) + a_prev)*dt
    end do
  end do
end subroutine iterate

function force(x, m, i, n_objs)
  implicit none
  real, intent(in) :: x(:,:)
  real, intent(in) :: m(:)
  integer, intent(in) :: i, n_objs

  real :: force(3)
  real, parameter :: g = 1
  integer :: j
  force = [0, 0, 0]

  do j=1,n_objs
    force = force + g*m(i)*m(j)*(x(:,i) - x(:,j)) / (x(:,i) - x(:,j))**3
  end do
end function force

program core
  print *, "Hello World!"
end program core
