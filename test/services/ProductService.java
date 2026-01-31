package services;

import entities.Product;
import repositories.ProductRepository;

public class ProductService {

    @Autowired
    private final ProductRepository productRepository;

    public ProductService(ProductRepository productRepository) {
        this.productRepository = productRepository;
    }

    public Product create(Long id, Product product) {
        product.setId(id);
        return productRepository.save(product);
    }

    public String listAll() {
        return productRepository.findAll().toString();
    }
}
