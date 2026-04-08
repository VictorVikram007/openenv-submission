# Data Cleaning & QA Environment

A realistic environment for evaluating AI agents on data quality assessment and cleaning tasks. Agents must handle missing values, type inconsistencies, duplicates, outliers, and referential integrity violations.

## 🎯 Overview

**Environment Name:** `data-cleaning-qa-env`  
**Task Domain:** Data Quality & ETL  
**Difficulty Range:** Easy → Medium → Hard  
**Episodes:** Single-step (one action per reset)

This environment simulates authentic data quality challenges that data analysts encounter in real projects—making it ideal for benchmarking AI systems on practical data engineering tasks.

---

## 📋 Tasks

### Task 1: Null Filling (Easy)
**Task ID:** `null_filling`

**Objective:** Fill missing values in a dataset using appropriate imputation strategies.

**Challenge Details:**
- Input: CSV with 100 rows, 5 columns
- Missing Rate: 15% (random nulls)
- Columns: `age`, `salary`, `department`, `city`, `score`

**Instruction:**
> Fill all null values in this CSV. Use column mean for numeric columns, mode for categorical columns.

**Ground Truth Logic:**
- Numeric cols (age, salary, score): Fill with column mean
- Categorical cols (department, city): Fill with column mode

**Example:**
```
BEFORE:
age,salary,department,city,score
25,,HR,New York,87.5
,,Engineering,London,
30,60000,,Paris,92.1

AFTER:
age,salary,department,city,score
25,85000,HR,New York,87.5
35,85000,Engineering,London,89.3
30,60000,Sales,Paris,92.1
```

**Grading Criteria:**
- Score = % of correctly filled cells
- Range: 0.0 (all wrong) to 1.0 (perfect)

---

### Task 2: Type Coercion & Deduplication (Medium)
**Task ID:** `type_coercion_dedup`

**Objective:** Fix data type inconsistencies and remove duplicate rows.

**Challenge Details:**
- Input: CSV with 200 rows, 4 columns
- Type Issues:
  - `salary`: Stored as string (should be float)
  - `sale_date`: Mixed date formats (YYYY-MM-DD, DD/MM/YYYY, MM-DD-YYYY)
  - `active`: Mixed representations (YES/NO, 1/0, True/False)
- Duplicates: ~10% of rows are exact duplicates

**Instruction:**
> Fix all data type issues and remove duplicate rows. Columns have mixed types. Some rows are exact duplicates. Return a clean CSV.

**Ground Truth Logic:**
- `salary`: Convert to float
- `sale_date`: Standardize to ISO format (YYYY-MM-DD)
- `active`: Convert to boolean
- Remove duplicate rows

**Grading Criteria:**
- Type Score: 50% if all dtypes match ground truth
- Dedup Score: 50% if duplicate count matches
- Total: 0.0-1.0

**Example:**
```
BEFORE (mixed types):
order_id,sale_date,salary,active
1,2023-01-01,500,YES
2,01/01/2023,500.50,1
2,2023-01-01,500.50,True

AFTER (clean):
order_id,sale_date,salary,active
1,2023-01-01,500.0,true
2,2023-01-01,500.5,true
```

---

### Task 3: Full QA Pipeline (Hard)
**Task ID:** `full_qa_pipeline`

**Objective:** Resolve multiple data quality issues across null handling, type fixing, deduplication, outlier detection, and referential integrity.

**Challenge Details:**
- Input: CSV with 500 rows, 5 columns
- Issues:
  1. **Nulls**: 10% missing in `age` column
  2. **Type Errors**: `salary` stored as mixed string/numeric
  3. **Duplicates**: 5% of rows are exact duplicates
  4. **Outliers**: Salary > 3σ (3 standard deviations)
  5. **Referential Integrity**: Invalid `dept_id` references (999 instead of valid 101-104)

**Instruction:**
> This dataset has multiple quality issues: nulls, type errors, duplicates, outliers (>3 std dev), and referential integrity violations. Fix ALL issues and return clean CSV with an issues_report.

**Ground Truth Logic:**
- Fill nulls with column mean
- Convert salary to float
- Remove duplicates
- Remove outliers (keep ±3σ range)
- Remove rows with invalid dept_id references

**Schema:**
```python
{
  "user_id": int,
  "name": str,
  "age": float,
  "salary": float,
  "dept_id": int (references 101-104)
}
```

**Grading Criteria (Weighted):**
- Null fixing: 25%
- Type fixing: 20%
- Duplicate removal: 20%
- Outlier handling: 20%
- Referential integrity: 15%
- Total: 0.0-1.0

---

## 📊 Observation Space

```python
{
  # Task metadata
  "task_id": str,              # "null_filling", "type_coercion_dedup", "full_qa_pipeline"
  "step": int,                 # Current step (0 on reset)
  "task_instruction": str,     # Natural language instruction
  "done": bool,                # False on reset, True after step()
  
  # Problem-specific
  "dirty_csv": str,            # CSV with quality issues (plain text)
  "schema": dict,              # {"col_name": "dtype", ...}
  "null_count": int            # Total nulls in dataset
}
```

### Example Observation:
```python
{
  "task_id": "null_filling",
  "step": 0,
  "task_instruction": "Fill all null values in this CSV. Use column mean for numeric columns, mode for categorical columns.",
  "done": False,
  "dirty_csv": "age,salary,department,city,score\n25,,HR,New York,87.5\n...",
  "schema": {
    "age": "int64",
    "salary": "float64",
    "department": "object",
    "city": "object",
    "score": "float64"
  },
  "null_count": 15
}
```

---

## ✏️ Action Space

```python
{
  "cleaned_csv": str,          # Required: Cleaned CSV (plain text, UTF-8)
  "issues_found": list,        # Optional: Issues identified in dirty_csv
  "transformations": list      # Optional: Transformations applied
}
```

### Example Action:
```python
{
  "cleaned_csv": "age,salary,department,city,score\n25,85000,HR,New York,87.5\n35,85000,Engineering,London,89.3\n...",
  "issues_found": ["null_filling"],
  "transformations": ["mean_imputation"]
}
```

---

## 🏆 Reward Function

The reward function provides **immediate, step-by-step feedback** on data quality improvements:

### Null Filling Task
```python
# Compare filled values to ground truth
score = (correct_fills / total_fills)
# Range: 0.0 (all wrong) to 1.0 (perfect)
```

### Type Coercion & Dedup Task
```python
# Weighted combination
type_score = 0.5 if dtypes_match else 0.0
dedup_score = 0.5 if dup_count_correct else 0.0
reward = type_score + dedup_score
# Range: 0.0, 0.5, 1.0
```

### Full QA Pipeline Task
```python
weights = {
  "nulls_fixed": 0.25,
  "types_fixed": 0.20,
  "duplicates_removed": 0.20,
  "outliers_handled": 0.20,
  "integrity_fixed": 0.15
}
# Weighted sum of individual scores
reward = sum(weights[issue] * score_for_issue)
# Range: 0.0 to 1.0
```

---

## 🚀 API Usage

### Reset Environment

```bash
curl -X POST http://localhost:7860/reset \
  -H "Content-Type: application/json" \
  -d '{"task_name": "null_filling"}'
```

**Response:**
```json
{
  "observation": {
    "task_id": "null_filling",
    "step": 0,
    "task_instruction": "Fill all null values...",
    "done": false,
    "dirty_csv": "age,salary,...",
    "schema": {"age": "int64", ...},
    "null_count": 15
  },
  "reward": 0.0,
  "done": false,
  "info": {}
}
```

### Submit Action

```bash
curl -X POST http://localhost:7860/step \
  -H "Content-Type: application/json" \
  -d '{
    "cleaned_csv": "age,salary,...",
    "issues_found": [],
    "transformations": []
  }'
```

**Response:**
```json
{
  "observation": {
    "task_id": "null_filling",
    "step": 1,
    "done": true,
    "dirty_csv": "",
    "schema": {}
  },
  "reward": 0.92,
  "done": true,
  "info": {"score_breakdown": {}}
}
```

### Get State

```bash
curl http://localhost:7860/state
```

---

## 💻 Running Locally

### Setup

```bash
cd env_a_data_cleaning

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

# Reset
resp = requests.post("http://localhost:7860/reset", json={"task_name": "null_filling"})
obs = resp.json()["observation"]

# Process
import pandas as pd
from io import StringIO

df = pd.read_csv(StringIO(obs["dirty_csv"]))
# ... your cleaning logic ...
cleaned_csv = df.to_csv(index=False)

# Submit
action = {
    "cleaned_csv": cleaned_csv,
    "issues_found": [],
    "transformations": []
}
result = requests.post("http://localhost:7860/step", json=action).json()
print(f"Reward: {result['reward']}")
```

---

## 📦 Docker Deployment

### Build

```bash
docker build -t meta-data-cleaning:latest .
```

### Run

```bash
docker run -p 7860:7860 \
  -e HF_TOKEN=sk_test_example \
  meta-data-cleaning:latest
```

---

## 🔬 Baseline Performance

Using GPT-4 with the OpenAI API:

| Task | Reward | Time | Issues |
|------|--------|------|--------|
| null_filling | 0.82 | 1.2s | None |
| type_coercion_dedup | 0.71 | 2.1s | Partial type conversion |
| full_qa_pipeline | 0.58 | 3.5s | Outlier detection challenges |
| **Average** | **0.70** | **2.3s** | - |

**Inference Command:**
```bash
export HF_TOKEN=sk_test_example
export MODEL_NAME=gpt-4
python inference.py
```

---

## 📄 Implementation Details

### Data Generation

Uses **deterministic data generation** with fixed random seed (42):

```python
np.random.seed(42)
```

Ensures:
- Same CSV generated for same task
- Reproducible baseline scores
- Fair evaluation across models

### Grading

All graders inherit from base grading interface:

```python
class NullFillingGrader:
    def score(self, cleaned_csv: str, ground_truth_csv: str) -> float:
        # Returns 0.0 to 1.0
        pass
```

### State Management

Episodes are **single-step**:
1. `reset()` → Start with dirty data
2. `step()` → Submit cleaned data, receive reward
3. Episode done

---

## 🎓 Evaluation Tips

1. **Parse CSV carefully** - Handle missing values, type mismatches
2. **Validate output** - Ensure cleaned CSV is valid
3. **Use appropriate imputation** - Mean for numeric, mode for categorical
4. **Remove true duplicates** - Exact row matches
5. **Detect outliers** - Use 3σ rule for continuous data

---

## ⚙️ Configuration

### Modify Task Difficulty

Edit `tasks.py`:
```python
TASK_1 = {
    "null_rate": 0.15,   # ← Change this
    "rows": 100,
    "columns": [...]
}
```

### Customize Grading

Edit `graders.py` to adjust scoring weights and criteria.

---

## 📚 References

- Pandas Documentation: https://pandas.pydata.org/docs/
- Data Quality Standards: https://en.wikipedia.org/wiki/Data_quality
- OpenEnv Spec: https://github.com/allenai/openenv
