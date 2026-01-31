package repositories;

import entities.User;
import java.util.HashMap;
import java.util.Map;

@Repository
public class UserRepository {

    private final Map<Long, User> db = new HashMap<>();

    public User save(User user) {
        db.put(user.getId(), user);
        return user;
    }

    public User findById(Long id) {
        return db.get(id);
    }

    @Query("select u from User u where u.status = ?1")
    public Map<Long, User> findAll(String status) {
        return db;
    }

    @Query("select u from User u where u.status = ?1")
    List<User> getUserByStatus(String status);
}
