module core
  implicit none
  ! Setting these on the module level did not pass F2PY compilation
  ! integer, parameter :: DIMS = 3
  ! integer, parameter :: REAL_KIND = 8
  ! real(kind=REAL_KIND), parameter :: G = 1
  ! real(kind=REAL_KIND), parameter :: MIN_DIST = 0.01
contains
  function force(x, m, i, n_objs)
    implicit none
    integer, parameter :: DIMS = 3
    integer, parameter :: REAL_KIND = 8
    real(kind=REAL_KIND), parameter :: G = 1
    real(kind=REAL_KIND), parameter :: MIN_DIST = 0.01

    integer, intent(in) :: i, n_objs
    real(kind=REAL_KIND), intent(in) :: x(DIMS,n_objs)
    real(kind=REAL_KIND), intent(in) :: m(n_objs)

    real(kind=REAL_KIND) :: force(DIMS), dist
    ! real(kind=REAL_KIND), parameter :: g = 1, min_dist = 0.01
    integer :: j
    force = 0

    do j=1,n_objs
      dist = sqrt(sum((x(:,i) - x(:,j))**2))
      ! Clipping prevents overflow
      if (dist > MIN_DIST) then
        force = force + G*m(i)*m(j)*(x(:,j) - x(:,i)) / dist**3
      end if
    end do
  end function force

  subroutine iterate(x, v, a, m, dt, n_steps, n_objs)
    ! Note that on Python side the argument n_objs is optional, since it can be automatically determined from the input arrays
    implicit none
    integer, parameter :: DIMS = 3
    integer, parameter :: REAL_KIND = 8

    ! Double precision is used for NumPy compatibility and more accurate results
    integer, intent(in) :: n_steps, n_objs
    real(kind=REAL_KIND), intent(inout) :: x(DIMS,n_objs)
    real(kind=REAL_KIND), intent(inout) :: v(DIMS,n_objs)
    real(kind=REAL_KIND), intent(inout) :: a(DIMS,n_objs)
    real(kind=REAL_KIND), intent(in) :: m(n_objs)
    real(kind=REAL_KIND), intent(in) :: dt

    integer :: i, iter
    real(kind=REAL_KIND) :: a_prev(DIMS)

    do iter=1,n_steps
      x = x + v*dt + 0.5*a*dt**2
      do i=1,n_objs
        a_prev = a(:,i)
        a(:,i) = force(x, m, i, n_objs) / m(i)
        v(:,i) = v(:,i) + 0.5*(a(:,i) + a_prev)*dt
      end do
    end do
  end subroutine iterate
end module core
