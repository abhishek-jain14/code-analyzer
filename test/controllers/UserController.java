package controllers;

import org.springframework.web.bind.annotation.*;
import services.UserService;
import entities.User;

@RestController
@RequestMapping("/api/user")
public class UserController {

    @Autowired
    private final UserService userService;

    @GetMapping("/list")
    public String listUsers() {
        return userService.listAll();
    }

     @GetMapping("/user/{id}")
    public String listUsers(@PathVariable Long id) {
        return userService.getUserById(id);
    }

    @PostMapping("/create/{id}")
    public User createUser(
        @PathVariable Long id,
        @RequestBody User user,
        @RequestParam String source
    ) {
        return userService.create(id, user);
    }
}
