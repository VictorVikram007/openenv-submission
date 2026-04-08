# Code Review & Bug Fixing Environment

A realistic environment for evaluating AI agents on code review tasks. Agents must identify bugs, security vulnerabilities, performance issues, and other code quality problems in Python codebases.

## 🎯 Overview

**Environment Name:** `code-review-bug-fixing-env`  
**Task Domain:** Code Review & Quality Assurance  
**Language:** Python  
**Difficulty Range:** Easy → Medium → Hard  
**Episodes:** Single-step (one review per reset)

This environment simulates authentic code review scenarios where AI agents must identify logic bugs, security flaws, performance bottlenecks, and design issues—essential for maintaining code quality and security.

---

## 📋 Tasks

### Task 1: Bug Detection (Easy)
**Task ID:** `bug_detection`

**Objective:** Identify a single bug in a Python function and provide a fix.

**Challenge Details:**
- Input: Single function with one deliberate bug
- Bug Types: Off-by-one, wrong operator, uninitialized variable, wrong return type
- Lines of Code: ~10-15 lines
- Difficulty: Clear, obvious bug

**Instruction:**
> Find the bug in this code. Return JSON with: bug_line (int), bug_type (str), explanation (str), fixed_code (str)

**Example:**
```python
# BUGGY CODE
def binary_search(arr, target):
    low = 0
    high = len(arr)  # ← BUG: Should be len(arr) - 1
    while low <= high:
        mid = (low + high) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1
```

**Expected Response:**
```json
{
  "bug_line": 3,
  "bug_type": "off_by_one",
  "explanation": "The 'high' variable is initialized to len(arr), which is out of bounds for a zero-indexed array. It should be len(arr) - 1.",
  "fixed_code": "def binary_search(arr, target):\n    low = 0\n    high = len(arr) - 1\n    ..."
}
```

**Grading Criteria:**
- Correct line number: +0.4
- Correct bug type: +0.3
- Valid fixed code (parseable Python): +0.3
- Total: 0.0-1.0

---

### Task 2: Security Review (Medium)
**Task ID:** `security_review`

**Objective:** Identify security vulnerabilities in a Flask API endpoint.

**Challenge Details:**
- Input: Flask API with ~15-20 lines
- Vulnerability Types: SQL Injection, hardcoded secrets, missing auth, path traversal, XSS
- Number of Bugs: 3-5 distinct vulnerabilities
- Difficulty: Requires security knowledge

**Instruction:**
> Review this API endpoint for security issues. Return JSON with: vulnerabilities (list of {type, line, severity, description, fix})

**Example:**
```python
# VULNERABLE CODE
from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)
API_SECRET = "sk-prod-12345"  # ← BUG 1: Hardcoded secret

@app.route('/user/<user_id>')  # ← BUG 2: Missing @login_required
def get_user(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # ← BUG 3: SQL Injection
    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor.execute(query)
    user = cursor.fetchone()
    
    conn.close()
    return jsonify(user)
```

**Expected Response:**
```json
{
  "vulnerabilities": [
    {
      "type": "hardcoded_secret",
      "line": 6,
      "severity": "high",
      "description": "API secret is hardcoded in the source file.",
      "fix": "Load the secret from environment variables or a secure vault."
    },
    {
      "type": "missing_auth",
      "line": 9,
      "severity": "critical",
      "description": "The endpoint is missing authentication checks.",
      "fix": "Add @login_required decorator to ensure only authenticated users can access it."
    },
    {
      "type": "sql_injection",
      "line": 14,
      "severity": "critical",
      "description": "SQL query is constructed using an f-string, vulnerable to injection.",
      "fix": "Use parameterized queries: cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))"
    }
  ]
}
```

**Grading Criteria:**
- Per vulnerability found: +1/N where N = total vulnerabilities
- Correct severity: +0.1 bonus per vulnerability
- Total: 0.0-1.0

---

### Task 3: Full PR Review (Hard)
**Task ID:** `full_pr_review`

**Objective:** Conduct comprehensive review of multi-file pull request with diverse issue types.

**Challenge Details:**
- Input: Diff across 3-5 files
- Issue Types: Logic bugs, performance problems, missing tests, code style, security issues
- Total Issues: 5-8 across all files
- Difficulty: Requires holistic understanding, multiple issue categories

**Instruction:**
> Review this pull request diff across 3 files. Return JSON with: summary (str), issues (list of {file, line, type, severity, description, suggestion}), overall_quality_score (0-10)

**Example PR Diff:**

```diff
diff --git a/auth.py b/auth.py
--- a/auth.py
+++ b/auth.py
@@ -10,7 +10,7 @@
 def is_token_valid(token):
     payload = decode_token(token)
     expiry = payload.get('exp')
-    if not expiry or expiry < time.time():  # ← BUG: Wrong comparison
+    if not expiry or expiry <= time.time():
         return False
     return True

diff --git a/database.py b/database.py
--- a/database.py
+++ b/database.py
@@ -25,8 +25,9 @@
 def get_user_profiles(user_ids):
     profiles = []
     for user_id in user_ids:  # ← PERF: N+1 query problem
-        user = db.session.query(User).filter_by(id=user_id).one()
-        profiles.append(user.profile)
+    # Fix: Use single query
+    users = db.session.query(User).filter(User.id.in_(user_ids)).all()
+    for user in users:
+        profiles.append(user.profile)
     return profiles
```

**Expected Response:**
```json
{
  "summary": "This PR introduces several critical issues including a logic bug in token validation, a performance bottleneck in the database layer, and missing input validation.",
  "issues": [
    {
      "file": "auth.py",
      "line": 12,
      "type": "logic_bug",
      "severity": "high",
      "description": "Token expiry check is incorrect. Uses '<' instead of '<=' causing valid tokens to be rejected.",
      "suggestion": "Change the condition to 'expiry <= time.time()' to correctly invalidate expired tokens."
    },
    {
      "file": "database.py",
      "line": 28,
      "type": "performance",
      "severity": "medium",
      "description": "N+1 query problem. Runs one database query per user instead of a single batch query.",
      "suggestion": "Use User.id.in_(user_ids) to fetch all users in a single query."
    }
  ],
  "overall_quality_score": 4
}
```

**Grading Criteria (Weighted):**
- Issues identified: 40% (% of planted issues found)
- Severity accuracy: 30% (% with correct severity)
- Suggestion quality: 30% (% with actionable suggestions)
- Total: 0.0-1.0

---

## 📊 Observation Space

```python
{
  # Task metadata
  "task_id": str,              # "bug_detection", "security_review", "full_pr_review"
  "step": int,                 # Current step (0 on reset)
  "task_instruction": str,     # Natural language instruction
  "done": bool,                # False on reset, True after step()
  
  # Problem-specific
  "code_snippet": str,         # Code to review (function or diff)
  "language": str,             # Programming language (e.g., "python")
  "filename": str,             # Original filename
  "task_type": str,            # Task category
  "context": str               # Additional context
}
```

### Example Observation:
```python
{
  "task_id": "bug_detection",
  "step": 0,
  "task_instruction": "Find the bug in this code. Return JSON with: bug_line (int), bug_type (str), explanation (str), fixed_code (str)",
  "done": False,
  "code_snippet": "def binary_search(arr, target):\n    low = 0\n    high = len(arr)\n    ...",
  "language": "python",
  "filename": "search.py",
  "task_type": "bug_detection",
  "context": "Review the following code snippet carefully."
}
```

---

## ✏️ Action Space

```python
{
  "response_json": dict        # Required: Structured JSON response
}
```

### Response Format Varies by Task:

**Bug Detection:**
```python
{
  "response_json": {
    "bug_line": int,           # Line number with bug
    "bug_type": str,           # Type of bug
    "explanation": str,        # Why it's a bug
    "fixed_code": str          # Corrected code
  }
}
```

**Security Review:**
```python
{
  "response_json": {
    "vulnerabilities": [
      {
        "type": str,           # Vulnerability type
        "line": int,           # Line number
        "severity": str,       # "low", "medium", "high", "critical"
        "description": str,    # What's vulnerable
        "fix": str             # How to fix it
      },
      ...
    ]
  }
}
```

**Full PR Review:**
```python
{
  "response_json": {
    "summary": str,            # Overall assessment
    "issues": [
      {
        "file": str,           # Filename
        "line": int,           # Line number
        "type": str,           # Issue type
        "severity": str,       # "low", "medium", "high", "critical"
        "description": str,    # Issue description
        "suggestion": str      # Recommended fix
      },
      ...
    ],
    "overall_quality_score": int  # 0-10 score
  }
}
```

---

## 🏆 Reward Function

The reward function provides **deterministic, detailed feedback** on review quality:

### Bug Detection
```python
score = 0.0
if action["bug_line"] == ground_truth["bug_line"]:
    score += 0.4
if action["bug_type"] == ground_truth["bug_type"]:
    score += 0.3
if valid_python(action["fixed_code"]):
    score += 0.3
# Range: 0.0 to 1.0
```

### Security Review
```python
found_vulns = set(action["vulnerability_types"])
ground_truth_vulns = set(ground_truth["vulnerability_types"])
overlap = len(found_vulns & ground_truth_vulns)

per_vuln_score = 1.0 / len(ground_truth_vulns)
score = overlap * per_vuln_score

# Severity bonus
for vuln in overlap:
    if action[vuln]["severity"] == ground_truth[vuln]["severity"]:
        score += 0.1
# Range: 0.0 to 1.0
```

### Full PR Review
```python
weights = {
  "issues_identified": 0.40,
  "severity_accuracy": 0.30,
  "suggestion_quality": 0.30
}

# Calculate components
issues_score = found_issues / total_issues
severity_score = correct_severities / found_issues
suggestion_score = helpful_suggestions / found_issues

score = (weights["issues_identified"] * issues_score +
         weights["severity_accuracy"] * severity_score +
         weights["suggestion_quality"] * suggestion_score)
# Range: 0.0 to 1.0
```

---

## 🚀 API Usage

### Reset Environment

```bash
curl -X POST http://localhost:7860/reset \
  -H "Content-Type: application/json" \
  -d '{"task_name": "bug_detection"}'
```

**Response:**
```json
{
  "observation": {
    "task_id": "bug_detection",
    "step": 0,
    "task_instruction": "Find the bug...",
    "done": false,
    "code_snippet": "def binary_search(arr, target):\n    ...",
    "language": "python",
    "filename": "search.py"
  },
  "reward": 0.0,
  "done": false,
  "info": {}
}
```

### Submit Review

```bash
curl -X POST http://localhost:7860/step \
  -H "Content-Type: application/json" \
  -d '{
    "response_json": {
      "bug_line": 3,
      "bug_type": "off_by_one",
      "explanation": "...",
      "fixed_code": "..."
    }
  }'
```

**Response:**
```json
{
  "observation": {
    "task_id": "bug_detection",
    "step": 1,
    "done": true
  },
  "reward": 0.88,
  "done": true,
  "info": {}
}
```

---

## 💻 Running Locally

### Setup

```bash
cd env_b_code_review

# Create environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Start Server

```bash
uvicorn server:app --reload --port 7860
```

### Test API

```python
import requests
import json

# Reset
resp = requests.post("http://localhost:7860/reset", json={"task_name": "bug_detection"})
obs = resp.json()["observation"]

print("Code to review:")
print(obs["code_snippet"])

# Submit review
action = {
    "response_json": {
        "bug_line": 3,
        "bug_type": "off_by_one",
        "explanation": "The 'high' variable is out of bounds.",
        "fixed_code": "def binary_search(arr, target):\n    low = 0\n    high = len(arr) - 1\n    ..."
    }
}
result = requests.post("http://localhost:7860/step", json=action).json()
print(f"Reward: {result['reward']}")
```

---

## 📦 Docker Deployment

### Build

```bash
docker build -t meta-code-review:latest .
```

### Run

```bash
docker run -p 7860:7860 \
  -e HF_TOKEN=sk_test_example \
  meta-code-review:latest
```

---

## 🔬 Baseline Performance

Using GPT-4 with the OpenAI API:

| Task | Reward | Time | Performance |
|------|--------|------|-------------|
| bug_detection | 0.88 | 0.8s | Excellent |
| security_review | 0.75 | 1.5s | Good |
| full_pr_review | 0.62 | 2.2s | Fair |
| **Average** | **0.75** | **1.5s** | - |

**Inference Command:**
```bash
export HF_TOKEN=sk_test_example
export MODEL_NAME=gpt-4
python inference.py
```

---

## 📄 Implementation Details

### Code Generation

Uses **deterministic code generation** (no randomness):

```python
def _generate_off_by_one_bug():
    buggy_code = textwrap.dedent("""
    def binary_search(arr, target):
        low = 0
        high = len(arr)  # Bug: should be len(arr) - 1
        ...
    """)
    # Fixed version and ground truth always the same
```

Ensures:
- Same code for same task across runs
- Reproducible benchmark scores
- Fair evaluation

### Grading

All graders implement standardized interface:

```python
class MyGrader:
    def score(self, action: dict, ground_truth: dict) -> float:
        # Returns 0.0 to 1.0
        pass
```

### State Management

Episodes are **single-step**:
1. `reset()` → Receive code to review
2. `step()` → Submit review, receive reward
3. Episode done

---

## 🎓 Review Tips

1. **Read code carefully** - Understand context and flow
2. **Check edge cases** - Off-by-one, null pointers, empty collections
3. **Verify security** - SQL injection, hardcoded secrets, auth
4. **Analyze performance** - N+1 queries, inefficient loops
5. **Test syntax** - Ensure fixed code is valid Python
6. **Be specific** - Line numbers and concrete explanations

---

## ⚙️ Configuration

### Modify Task Content

Edit `code_generator.py` to change:
- Bug types and complexity
- Vulnerability categories
- Number of issues to plant

### Customize Grading

Edit `graders.py` to adjust:
- Scoring criteria
- Weighting of issue types
- Severity definitions

---

## 📚 References

- OWASP Top 10: https://owasp.org/www-project-top-ten/
- CWE: https://cwe.mitre.org/
- Code Review Best Practices: https://google.github.io/styleguide/
- OpenEnv Spec: https://github.com/allenai/openenv
