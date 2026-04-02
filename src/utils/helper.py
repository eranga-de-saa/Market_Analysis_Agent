import pandas as pd
import numpy as np


def make_json_safe(obj):

    if isinstance(obj, dict):
        return {str(k): make_json_safe(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_json_safe(v) for v in obj]
    elif isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    elif isinstance(obj, (np.integer, np.floating)):
        return float(obj)
    elif hasattr(obj, "item"):  # numpy scalar
        return obj.item()
    else:
        return obj