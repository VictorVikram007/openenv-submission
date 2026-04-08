# c:\Users\Vikram\OneDrive\Desktop\meta\openenv-submission\env_a_data_cleaning\data_generator.py
import pandas as pd
import numpy as np
from io import StringIO

def generate_dirty_csv(task_config: dict) -> tuple[str, str]:
    """
    Generates a tuple of (dirty_csv_string, clean_csv_string) based on the task config.
    Uses a fixed random seed for reproducibility.
    """
    np.random.seed(42)
    task_id = task_config["task_id"]

    if task_id == "null_filling":
        return _generate_null_filling_data(task_config)
    elif task_id == "type_coercion_dedup":
        return _generate_type_coercion_data(task_config)
    elif task_id == "full_qa_pipeline":
        return _generate_full_qa_data(task_config)
    else:
        raise ValueError(f"Unknown task_id: {task_id}")

def _generate_null_filling_data(config):
    rows = config['rows']
    cols = config['columns']
    data = {
        'age': np.random.randint(22, 65, size=rows),
        'salary': np.random.randint(50000, 150000, size=rows),
        'department': np.random.choice(['HR', 'Engineering', 'Sales', 'Marketing'], size=rows),
        'city': np.random.choice(['New York', 'London', 'Tokyo', 'Paris'], size=rows),
        'score': np.random.uniform(0, 100, size=rows).round(2)
    }
    df = pd.DataFrame(data, columns=cols)
    clean_df = df.copy()

    dirty_df = df.copy()
    for col in dirty_df.columns:
        mask = np.random.rand(len(dirty_df)) < config['null_rate']
        dirty_df.loc[mask, col] = np.nan
    
    # Fill clean_df with correct values for ground truth
    for col in clean_df.columns:
        if pd.api.types.is_numeric_dtype(clean_df[col]):
            mean_val = clean_df[col].mean()
            dirty_df_col_copy = dirty_df[col].copy()
            dirty_df_col_copy.fillna(mean_val, inplace=True)
            clean_df.loc[dirty_df[col].isnull(), col] = mean_val
        else:
            mode_val = clean_df[col].mode()[0]
            dirty_df_col_copy = dirty_df[col].copy()
            dirty_df_col_copy.fillna(mode_val, inplace=True)
            clean_df.loc[dirty_df[col].isnull(), col] = mode_val


    return dirty_df.to_csv(index=False), clean_df.to_csv(index=False)


def _generate_type_coercion_data(config):
    rows = config['rows']
    df = pd.DataFrame({
        'order_id': range(rows),
        'sale_date': pd.to_datetime(pd.date_range('2023-01-01', periods=rows)),
        'salary': np.random.uniform(300, 1000, size=rows).round(2),
        'active': np.random.choice([True, False], size=rows)
    })
    clean_df = df.copy()
    
    dirty_df = df.copy()
    
    # Introduce type errors
    dirty_df['salary'] = dirty_df['salary'].astype(str)
    
    date_formats = ["%Y-%m-%d", "%d/%m/%Y", "%m-%d-%Y %H:%M:%S"]
    for i in range(len(dirty_df)):
        dirty_df.loc[i, 'sale_date'] = dirty_df.loc[i, 'sale_date'].strftime(np.random.choice(date_formats))

    active_map = {True: 'YES', False: 'NO'}
    active_choices = ['YES', 'NO', '1', '0', 'True', 'False']
    dirty_df['active'] = np.random.choice(active_choices, size=rows)


    # Introduce duplicates
    num_dupes = int(rows * config['duplicate_rate'])
    dupe_indices = np.random.choice(df.index, size=num_dupes, replace=False)
    dupes = dirty_df.loc[dupe_indices]
    dirty_df = pd.concat([dirty_df, dupes]).sample(frac=1).reset_index(drop=True)

    clean_df['active'] = clean_df['active'].astype(bool)
    
    return dirty_df.to_csv(index=False), clean_df.drop_duplicates().to_csv(index=False)


def _generate_full_qa_data(config):
    rows = config['rows']
    
    # Main entity table
    users = pd.DataFrame({
        'user_id': range(1, rows + 1),
        'name': [f'user_{i}' for i in range(rows)],
        'age': np.random.randint(18, 70, size=rows),
        'salary': np.random.normal(75000, 15000, size=rows).round(2)
    })
    
    # Referential table
    departments = pd.DataFrame({
        'dept_id': [101, 102, 103, 104],
        'dept_name': ['Engineering', 'Sales', 'HR', 'Marketing']
    })
    
    users['dept_id'] = np.random.choice(departments['dept_id'], size=rows)
    
    clean_df = users.copy()
    dirty_df = users.copy()

    # 1. Nulls
    dirty_df.loc[dirty_df.sample(frac=0.1, random_state=42).index, 'age'] = np.nan
    
    # 2. Type Errors
    dirty_df['salary'] = dirty_df['salary'].astype(str)
    
    # 3. Duplicates
    dupes = dirty_df.sample(frac=0.05, random_state=42)
    dirty_df = pd.concat([dirty_df, dupes]).reset_index(drop=True)
    
    # 4. Outliers
    outlier_indices = dirty_df.sample(n=5, random_state=42).index
    dirty_df.loc[outlier_indices, 'salary'] = dirty_df.loc[outlier_indices, 'salary'].astype(float) * 5 # create outliers
    dirty_df['salary'] = dirty_df['salary'].astype(str)


    # 5. Referential Integrity
    bad_dept_indices = dirty_df.sample(frac=0.05, random_state=42).index
    dirty_df.loc[bad_dept_indices, 'dept_id'] = 999 # Invalid dept_id
    
    # Create ground truth by fixing issues
    clean_df['age'].fillna(clean_df['age'].mean(), inplace=True)
    clean_df['salary'] = clean_df['salary'].astype(float)
    clean_df.drop_duplicates(inplace=True)
    
    # Remove outliers from clean_df
    mean = clean_df['salary'].mean()
    std = clean_df['salary'].std()
    clean_df = clean_df[np.abs(clean_df['salary'] - mean) <= (3 * std)]

    # Fix referential integrity
    valid_dept_ids = departments['dept_id']
    clean_df = clean_df[clean_df['dept_id'].isin(valid_dept_ids)]

    return dirty_df.to_csv(index=False), clean_df.to_csv(index=False)
