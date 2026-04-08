# c:\Users\Vikram\OneDrive\Desktop\meta\openenv-submission\env_b_code_review\tasks.py
TASK_1 = {
  "task_id": "bug_detection",
  "difficulty": "easy",
  "language": "python",
  "instruction": "Find the bug in this code. Return JSON with: bug_line (int), bug_type (str), explanation (str), fixed_code (str)",
  "bug_types": ["off_by_one", "wrong_operator", "uninitialized_variable", "wrong_return_type"]
}

TASK_2 = {
  "task_id": "security_review", 
  "difficulty": "medium",
  "language": "python",
  "instruction": "Review this API endpoint for security issues. Return JSON with: vulnerabilities (list of {type, line, severity, description, fix})",
  "vulnerability_types": ["sql_injection", "hardcoded_secret", "missing_auth", "path_traversal", "xss_vulnerability"]
}

TASK_3 = {
  "task_id": "full_pr_review",
  "difficulty": "hard", 
  "language": "python",
  "instruction": "Review this pull request diff across 3 files. Return JSON with: summary (str), issues (list of {file, line, type, severity, description, suggestion}), overall_quality_score (0-10)",
  "issue_types": ["logic_bug", "performance", "missing_tests", "style", "security"]
}

TASKS = {
    "bug_detection": TASK_1,
    "security_review": TASK_2,
    "full_pr_review": TASK_3,
}
