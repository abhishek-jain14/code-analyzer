package com.example.soap;

import javax.jws.WebMethod;
import javax.jws.WebService;

@WebService
public class UserSoapService {

     @Autowired
    private final UserRepository userRepository;

    @WebMethod
    public User createUser(User user) {
        userValidation.validateUser(user);
        userValidation.validatePermission(user);

        // persist user
        return userRepository.save(user);
    }

    @WebMethod
    public User getUserById(Long id) {
        // fetch user
        return new User();
    }

    @WebMethod
    public boolean deleteUser(Long id) {
        // delete user
        return true;
    }
}
