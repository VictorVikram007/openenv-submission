# c:\Users\Vikram\OneDrive\Desktop\meta\openenv-submission\env_b_code_review\code_generator.py
import textwrap

def generate_buggy_code(task_config: dict) -> tuple[str, dict]:
    """
    Generates a tuple of (buggy_code_string, ground_truth_dict) based on the task config.
    This is deterministic and does not use randomness.
    """
    task_id = task_config["task_id"]

    if task_id == "bug_detection":
        return _generate_off_by_one_bug()
    elif task_id == "security_review":
        return _generate_security_flaw_code()
    elif task_id == "full_pr_review":
        return _generate_pr_diff_code()
    else:
        raise ValueError(f"Unknown task_id: {task_id}")

def _generate_off_by_one_bug():
    buggy_code = textwrap.dedent("""
    def binary_search(arr, target):
        low = 0
        high = len(arr)  # Bug: should be len(arr) - 1
        while low <= high:
            mid = (low + high) // 2
            if arr[mid] == target:
                return mid
            elif arr[mid] < target:
                low = mid + 1
            else:
                high = mid - 1
        return -1
    """)
    
    fixed_code = buggy_code.replace("high = len(arr)", "high = len(arr) - 1")
    
    ground_truth = {
        "bug_line": 3,
        "bug_type": "off_by_one",
        "explanation": "The 'high' variable is initialized to len(arr), which is out of bounds for a zero-indexed array. It should be len(arr) - 1.",
        "fixed_code": fixed_code.strip()
    }
    return buggy_code.strip(), ground_truth

def _generate_security_flaw_code():
    buggy_code = textwrap.dedent("""
    from flask import Flask, request, jsonify
    import sqlite3

    app = Flask(__name__)
    API_SECRET = "sk-prod-12345" # Bug 1: Hardcoded secret

    # Bug 2: Missing @login_required decorator
    @app.route('/user/<user_id>')
    def get_user(user_id):
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        
        # Bug 3: SQL Injection
        query = f"SELECT * FROM users WHERE id = {user_id}"
        cursor.execute(query)
        user = cursor.fetchone()
        
        conn.close()
        return jsonify(user)
    """)
    
    ground_truth = {
        "vulnerabilities": [
            {"type": "hardcoded_secret", "line": 6, "severity": "high", "description": "API secret is hardcoded in the source file.", "fix": "Load the secret from environment variables or a secure vault."},
            {"type": "missing_auth", "line": 9, "severity": "critical", "description": "The endpoint is missing authentication and authorization checks.", "fix": "Add a decorator like @login_required to ensure only authenticated users can access it."},
            {"type": "sql_injection", "line": 14, "severity": "critical", "description": "The SQL query is constructed using an f-string, making it vulnerable to SQL injection.", "fix": "Use parameterized queries to safely pass the user_id."},
        ]
    }
    return buggy_code.strip(), ground_truth

def _generate_pr_diff_code():
    diff = textwrap.dedent("""
    diff --git a/auth.py b/auth.py
    --- a/auth.py
    +++ b/auth.py
    @@ -10,7 +10,7 @@
     def is_token_valid(token):
         payload = decode_token(token)
         expiry = payload.get('exp')
    -    if not expiry or expiry < time.time(): # Bug: Should be expiry > time.time()
    +    if not expiry or expiry <= time.time():
             return False
         return True
 
    diff --git a/database.py b/database.py
    --- a/database.py
    +++ b/database.py
    @@ -25,8 +25,9 @@
     def get_user_profiles(user_ids):
         profiles = []
         for user_id in user_ids:
    -        # Bug: N+1 query problem
    -        user = db.session.query(User).filter_by(id=user_id).one()
    -        profiles.append(user.profile)
    +    # Fix: Use a single query to fetch all users
    +    users = db.session.query(User).filter(User.id.in_(user_ids)).all()
    +    for user in users:
    +        profiles.append(user.profile)
         return profiles
 
    diff --git a/api.py b/api.py
    --- a/api.py
    +++ b/api.py
    @@ -50,6 +50,9 @@
     @app.route('/users/update', methods=['POST'])
     def update_user():
         data = request.get_json()
    +    # Bug: Missing input validation
    +    if not data.get('email') or not data.get('name'):
    +        return jsonify({"error": "Missing required fields"}), 400
         user_id = data.get('user_id')
         update_fields(user_id, data)
         return jsonify({"status": "success"})
    """)
    
    ground_truth = {
        "summary": "This PR introduces several critical issues including a logic bug in token validation, a performance bottleneck in the database layer, and a security vulnerability due to missing input validation.",
        "issues": [
            {"file": "auth.py", "line": 12, "type": "logic_bug", "severity": "high", "description": "Token expiry check is incorrect. It invalidates tokens that are still valid.", "suggestion": "The check should be `expiry <= time.time()`."},
            {"file": "database.py", "line": 28, "type": "performance", "severity": "medium", "description": "N+1 query problem in `get_user_profiles`. This will run one query for each user ID.", "suggestion": "Fetch all users in a single query using `User.id.in_(user_ids)`."},
            {"file": "api.py", "line": 53, "type": "security", "severity": "high", "description": "Missing input validation in `update_user` endpoint.", "suggestion": "Add validation to ensure required fields like 'email' and 'name' are present before processing."},
        ],
        "overall_quality_score": 3
    }
    return diff.strip(), ground_truth
