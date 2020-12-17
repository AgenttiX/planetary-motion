module core
contains
  function force(x, m, i, n_objs)
    implicit none
    integer, intent(in) :: i, n_objs
    real(kind=8), intent(in) :: x(3,n_objs)
    real(kind=8), intent(in) :: m(n_objs)

    real(kind=8) :: force(3), dist
    real(kind=8), parameter :: g = 1, min_dist = 0.01
    integer :: j
    force = [0, 0, 0]

    do j=1,n_objs
      dist = sqrt(sum((x(:,i) - x(:,j))**2))
      ! Clipping prevents overflow
      if (dist > min_dist) then
        force = force + g*m(i)*m(j)*(x(:,j) - x(:,i)) / dist**3
      end if
    end do
  end function force

  subroutine iterate(x, v, a, m, dt, n_iters, n_objs)
    ! Note that on Python side the argument n_objs is optional, since it can be automatically determined from the input arrays
    implicit none
    ! Double precision is used for NumPy compatibility and more accurate results
    integer, intent(in) :: n_iters, n_objs
    real(kind=8), intent(inout) :: x(3,n_objs)
    real(kind=8), intent(inout) :: v(3,n_objs)
    real(kind=8), intent(inout) :: a(3,n_objs)
    real(kind=8), intent(in) :: m(n_objs)
    real(kind=8), intent(in) :: dt

    integer :: i, iter
    real(kind=8) :: a_prev(3)

    do iter=1,n_iters
      x = x + v*dt + 0.5*a*dt**2
      do i=1,n_objs
        a_prev = a(:,i)
        a(:,i) = force(x, m, i, n_objs) / m(i)
        v(:,i) = v(:,i) + 0.5*(a(:,i) + a_prev)*dt
      end do
    end do
  end subroutine iterate
end module core
