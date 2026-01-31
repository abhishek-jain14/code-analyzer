package repositories;

import entities.Product;
import java.util.HashMap;
import java.util.Map;

@Repository
public class ProductRepository {

    private final Map<Long, Product> db = new HashMap<>();

    public Product save(Product product) {
        db.put(product.getId(), product);
        return product;
    }

    public Product findById(Long id) {
        return db.get(id);
    }

    public Map<Long, Product> findAll() {
        return db;
    }
}
