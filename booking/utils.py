import random
import string
from datetime import datetime

def generate_transaction_ref():
    date_str = datetime.now().strftime("%Y%m%d")  # Example: 20251114
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"CR{date_str}{random_str}"
