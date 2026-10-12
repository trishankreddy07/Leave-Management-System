"""
Root entry point proxying src.worker for backwards compatibility with Gunicorn/local setups.
"""
from src.worker import (
    app,
    init_db,
    get_db,
    DATABASE_PATH,
    Default,
    default,
    TOTAL_LEAVES,
    LEAVE_TYPES,
    INITIAL_EMPLOYEES
)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
