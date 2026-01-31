package controllers;

import org.springframework.web.bind.annotation.*;
import services.ProductService;
import entities.Product;

@RestController
@RequestMapping("/api/product")
public class ProductController {

    private final ProductService productService;

    public ProductController(ProductService productService) {
        this.productService = productService;
    }

    @GetMapping("/list")
    public String listProducts() {
        return productService.listAll();
    }

    @PostMapping("/create/{id}")
    public Product createProduct(
        @PathVariable Long id,
        @RequestBody Product product,
        @RequestParam String category
    ) {
        return productService.create(id, product);
    }
}
