from tree_sitter import Parser
from tree_sitter_languages import get_language

parser = Parser()
parser.set_language(get_language("java"))

code = b"""
@RestController
public class Test {
    @PostMapping("/hello")
    public void hello() {}
}
"""

tree = parser.parse(code)
print(tree.root_node)
