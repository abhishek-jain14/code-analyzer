package services;

import entities.User;
import repositories.UserRepository;

public class UserService {

    @Autowired
    private final UserRepository userRepository;

     @Autowired
    private final UserValidation userValidation;

    public User create(Long id, User user) {
        userValidation.validateUser(user);
        userValidation.validatePermission(user);
        user.setId(id);
        return userRepository.save(user);
        }

    public String listAll() {
        return userRepository.findAll("ACTIVE").toString();
    }

    public String getUserById(Long id) {
        User user = userRepository.findById(id);
        if (user == null) {
            return "User not found";
        }
        return user.toString();
    }
}
