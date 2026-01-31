public class UserValidation {
    public void validateUser(User user) {
        if (user.getAge() > 100) {
            throw new IllegalArgumentException("Invalid age");
        }

        if (user.getStatus() == Status.INACTIVE) {
            throw new BusinessException("Inactive user");
        }
    }

    public void validatePermission(User user) {
        if (user.getCreatedBy() == null || user.getCreatedBy().isEmpty()) {
            throw new IllegalArgumentException("Invalid user creator");
        }   
    }
}