# c:\Users\Vikram\OneDrive\Desktop\meta\openenv-submission\env_a_data_cleaning\tasks.py
TASK_1 = {
  "task_id": "null_filling",
  "difficulty": "easy",
  "instruction": "Fill all null values in this CSV. Use column mean for numeric columns, mode for categorical columns.",
  "null_rate": 0.15,
  "rows": 100,
  "columns": ["age", "salary", "department", "city", "score"]
}

TASK_2 = {
  "task_id": "type_coercion_dedup",
  "difficulty": "medium", 
  "instruction": "Fix all data type issues and remove duplicate rows. Columns have mixed types. Some rows are exact duplicates. Return a clean CSV.",
  "rows": 200,
  "duplicate_rate": 0.10,
  "type_errors": ["salary stored as string", "date stored as mixed formats", "active stored as YES/NO/1/0/True/False"]
}

TASK_3 = {
  "task_id": "full_qa_pipeline",
  "difficulty": "hard",
  "instruction": "This dataset has multiple quality issues: nulls, type errors, duplicates, outliers (>3 std dev), and referential integrity violations. Fix ALL issues and return clean CSV with an issues_report.",
  "rows": 500,
  "issues": ["nulls", "type_errors", "duplicates", "outliers", "referential_integrity"]
}

TASKS = {
    "null_filling": TASK_1,
    "type_coercion_dedup": TASK_2,
    "full_qa_pipeline": TASK_3,
}
