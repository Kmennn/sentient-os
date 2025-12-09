
from core.tools.registry import BaseTool, registry
import sympy

class CalculatorAdvancedTool(BaseTool):
    @property
    def name(self):
        return "calculator_advanced"

    @property
    def description(self):
        return "Perform advanced math (algebra, units) using SymPy. Params: 'expression' (str)."
    
    @property
    def category(self):
        return "math"

    def run(self, params):
        expr = params.get("expression", "")
        if not expr:
            return "Error: No expression provided"
        
        try:
            # Parse and eval
            # Sympy sympify is powerful but risky? 
            # We trust local user input.
            result = sympy.sympify(expr)
            return f"Result: {result} (Type: {type(result).__name__})"
        except Exception as e:
            return f"Math Error: {e}"

# Auto-register done by registry autodiscover if we import it?
# But registry uses 'autodiscover' which scans directory.
# So just saving this file is enough IF registry scans it.
# Registry scans 'core.tools'.
