# System Architecture

Technical overview of the Meta OpenEnv platform architecture, design patterns, and implementation details.

## 🌐 Live Deployment

**Try the environments online:**
- 🧹 [Data Cleaning & QA on HF Spaces](https://huggingface.co/spaces/vikram727/data-cleaning-qa-env)
- 🔍 [Code Review & Bug Fixing on HF Spaces](https://huggingface.co/spaces/vikram727/code-review-bug-fixing-env)

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Hugging Face Spaces (Optional)              │
│                      Docker Environment                      │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                   Gradio Interface                      │ │
│  │        (Interactive Benchmarking Dashboard)            │ │
│  └──────────┬──────────────┬──────────────────────────────┘ │
│             │              │                                 │
└─────────────┼──────────────┼─────────────────────────────────┘
              │              │
    ┌─────────▼──┐  ┌───────▼──────┐
    │ Data Clean │  │ Code Review  │
    │  FastAPI   │  │  FastAPI     │
    │  Server    │  │  Server      │
    │  (Port 8A)  │  │  (Port 8B)   │
    └──────┬──────┘  └────────┬─────┘
           │                  │
    ┌──────▼──────────────────▼──────┐
    │      Shared Components         │
    │  ├─ base_models.py             │
    │  │  (Pydantic Models)          │
    │  ├─ logging_utils.py           │
    │  └─ __init__.py                │
    └────────────────────────────────┘
```

---

## 📦 Component Structure

### Directory Layout

```
meta/
├── app.py                          # Gradio interface entry point
├── docker-compose.yml              # Full stack orchestration
├── Dockerfile.gradio               # Gradio container spec
├── requirements.txt                # Global dependencies
├── README.md                       # Main documentation
├── QUICKSTART.md                   # Quick start guide
├── DEPLOYMENT.md                   # Deployment instructions
├── ARCHITECTURE.md                 # This file
│
├── env_a_data_cleaning/
│   ├── __init__.py
│   ├── server.py                   # FastAPI app
│   ├── environment.py              # Core env implementation
│   ├── tasks.py                    # Task definitions
│   ├── data_generator.py           # Data generation logic
│   ├── graders.py                  # Scoring functions
│   ├── inference.py                # Baseline script
│   ├── openenv.yaml                # OpenEnv spec
│   ├── Dockerfile                  # Container spec
│   ├── requirements.txt            # Dependencies
│   └── README.md                   # Environment docs
│
├── env_b_code_review/
│   ├── __init__.py
│   ├── server.py                   # FastAPI app
│   ├── environment.py              # Core env implementation
│   ├── tasks.py                    # Task definitions
│   ├── code_generator.py           # Code generation logic
│   ├── graders.py                  # Scoring functions
│   ├── inference.py                # Baseline script
│   ├── openenv.yaml                # OpenEnv spec
│   ├── Dockerfile                  # Container spec
│   ├── requirements.txt            # Dependencies
│   └── README.md                   # Environment docs
│
└── shared/
    ├── __init__.py
    ├── base_models.py              # Pydantic models
    ├── logging_utils.py            # Logging utilities
    └── README.md                   # Shared docs
```

---

## 🔄 OpenEnv Lifecycle

### Episode Flow (Single-Step Tasks)

```
┌────────────────────────────────┐
│  1. Client Requests Reset      │
│     POST /reset                │
│     {"task_name": "..."}       │
└────────────────┬───────────────┘
                 │
                 ▼
┌────────────────────────────────┐
│  2. Environment Initializes    │
│     - Load task config         │
│     - Generate problem data    │
│     - Set initial state        │
└────────────────┬───────────────┘
                 │
                 ▼
┌────────────────────────────────┐
│  3. Return Initial Observation │
│     {                          │
│       observation: {...},      │
│       reward: 0.0,             │
│       done: false,             │
│       info: {}                 │
│     }                          │
└────────────────┬───────────────┘
                 │
                 ▼
┌────────────────────────────────┐
│  4. Agent Processes & Acts     │
│     (External to Environment)  │
└────────────────┬───────────────┘
                 │
                 ▼
┌────────────────────────────────┐
│  5. Client Submits Action      │
│     POST /step                 │
│     action: {...}             │
└────────────────┬───────────────┘
                 │
                 ▼
┌────────────────────────────────┐
│  6. Environment Evaluates      │
│     - Run grader               │
│     - Calculate reward         │
│     - Set done=true            │
└────────────────┬───────────────┘
                 │
                 ▼
┌────────────────────────────────┐
│  7. Return Final Observation   │
│     {                          │
│       observation: {...},      │
│       reward: 0.85,            │
│       done: true,              │
│       info: {}                 │
│     }                          │
└────────────────────────────────┘
```

---

## 🎯 Data Models (Pydantic)

### Base Classes (`shared/base_models.py`)

```python
class BaseObservation(BaseModel):
    task_id: str              # Task identifier
    step: int                 # Current step number
    task_instruction: str     # Natural language instruction
    done: bool                # Episode completion flag

class BaseAction(BaseModel):
    pass                      # Subclassed by environments

class BaseReward(BaseModel):
    score: float              # Numerical score (0.0-1.0)
    breakdown: dict           # Score components
    feedback: str             # Human-readable feedback

class StepResult(BaseModel):
    observation: dict         # Observation (serialized)
    reward: float             # Reward value
    done: bool                # Episode done flag
    info: dict                # Additional info
```

### Data Cleaning Models

```python
class DataCleaningObservation(BaseObservation):
    dirty_csv: str            # CSV with quality issues
    schema: dict              # Column dtypes
    null_count: int           # Total nulls

class DataCleaningAction(BaseAction):
    cleaned_csv: str          # Cleaned CSV
    issues_found: list        # Issues identified
    transformations: list     # Transformations applied
```

### Code Review Models

```python
class CodeReviewObservation(BaseObservation):
    code_snippet: str         # Code to review
    language: str             # Programming language
    filename: str             # Original filename
    task_type: str            # Task category
    context: str              # Additional context

class CodeReviewAction(BaseAction):
    response_json: dict       # Structured response
```

---

## 🎓 Grading System

### Grader Interface

All graders implement a standard interface:

```python
class BaseGrader:
    def score(self, action: Any, ground_truth: Any) -> float:
        """
        Score an action against ground truth.
        
        Args:
            action: Agent's submission
            ground_truth: Expected/reference output
            
        Returns:
            float: Score between 0.0 and 1.0
        """
        raise NotImplementedError
```

### Grading Architecture

```
┌─────────────────────────────────┐
│      Agent Submission           │
│    (cleaned_csv or JSON)        │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│    Grader Selection             │
│  (task_id → grader mapping)     │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│    Ground Truth Loading         │
│  (Generated in reset())         │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│    Scoring Computation          │
│  (Grader.score())              │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│    Reward Value                 │
│    0.0 ≤ reward ≤ 1.0          │
└─────────────────────────────────┘
```

### Scoring Methods

**Data Cleaning:**
- Null Filling: % of correct values
- Type Coercion: Type matching + dedup ratio
- Full QA: Weighted sum across 5 dimensions

**Code Review:**
- Bug Detection: Line + type + fix validity
- Security: Vulnerabilities found + severity
- PR Review: Issues identified + severity + suggestion quality

---

## 🔧 Environment Implementation

### Core Environment Class

```python
class DataCleaningEnv:
    def __init__(self):
        self.current_task_config = None
        self.dirty_df = None
        self.clean_df = None
        self.step_count = 0
        self.episode_done = False
        self.graders = {
            "null_filling": NullFillingGrader(),
            "type_coercion_dedup": TypeCoercionGrader(),
            "full_qa_pipeline": FullQAPipelineGrader(),
        }

    def reset(self, task_name: str) -> StepResult:
        """Initialize environment for a task"""
        self.current_task_config = TASKS[task_name]
        dirty_csv, clean_csv = generate_dirty_csv(self.current_task_config)
        self.dirty_df = pd.read_csv(StringIO(dirty_csv))
        self.clean_df = pd.read_csv(StringIO(clean_csv))
        self.step_count = 0
        self.episode_done = False
        
        obs = DataCleaningObservation(
            task_id=task_name,
            step=0,
            task_instruction=self.current_task_config["instruction"],
            done=False,
            dirty_csv=dirty_csv,
            schema=self.dirty_df.dtypes.apply(lambda x: x.name).to_dict(),
            null_count=int(self.dirty_df.isnull().sum().sum())
        )
        
        return StepResult(
            observation=obs.model_dump(),
            reward=0.0,
            done=False,
            info={}
        )

    def step(self, action: DataCleaningAction) -> StepResult:
        """Process action and return reward"""
        self.step_count += 1
        task_id = self.current_task_config["task_id"]
        grader = self.graders[task_id]
        
        ground_truth_csv = self.clean_df.to_csv(index=False)
        score = grader.score(action.cleaned_csv, ground_truth_csv)
        self.episode_done = True
        
        obs = DataCleaningObservation(
            task_id=task_id,
            step=self.step_count,
            task_instruction=self.current_task_config["instruction"],
            done=True,
            dirty_csv="",
            schema={},
            null_count=0
        )
        
        return StepResult(
            observation=obs.model_dump(),
            reward=score,
            done=True,
            info={"score_breakdown": {}}
        )

    def state(self) -> dict:
        """Return current environment state"""
        return {
            "task_config": self.current_task_config,
            "step_count": self.step_count,
            "episode_done": self.episode_done,
        }
```

---

## 🌐 API Design (FastAPI)

### Endpoints

```python
@app.post("/reset", response_model=StepResult)
def reset(request: ResetRequest):
    """Reset environment and start new episode"""
    return env.reset(request.task_name)

@app.post("/step", response_model=StepResult)
def step(action: DataCleaningAction):
    """Process action and return reward"""
    return env.step(action)

@app.get("/state")
def state():
    """Get current environment state"""
    return env.state()

@app.get("/health")
def health():
    """Health check endpoint"""
    return {"status": "ok"}
```

### Request/Response Flow

```
Request (JSON)
    ↓
FastAPI Validation (Pydantic)
    ↓
Route Handler (Endpoint Function)
    ↓
Environment Method Call
    ↓
Grading (if step())
    ↓
StepResult Creation
    ↓
Response (JSON)
```

---

## 📊 Data Generation

### Deterministic Generation

```python
def generate_dirty_csv(task_config: dict) -> Tuple[str, str]:
    """Generate dirty and clean CSV pair"""
    np.random.seed(42)  # Fixed seed for reproducibility
    
    # Generate data
    # Apply issue injection
    # Return (dirty_csv, clean_csv)
```

**Benefits:**
- Same task always produces same data
- Reproducible baselines
- Fair evaluation across models
- Deterministic testing

### Generation Pipeline

```
┌──────────────────┐
│  Task Config     │
│  {rows, cols}    │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ np.random.seed   │
│ (42)             │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Base Data Gen    │
│ (rows × cols)    │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Issue Injection  │
│ (nulls, types,   │
│  duplicates)     │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Dirty CSV        │
│ + Clean CSV      │
└──────────────────┘
```

---

## 🐳 Containerization

### Container Architecture

```
┌──────────────────────────────────────┐
│    Dockerfile                        │
├──────────────────────────────────────┤
│ FROM python:3.11-slim                │
│ WORKDIR /app                         │
│ COPY requirements.txt .              │
│ RUN pip install ...                  │
│ COPY . .                             │
│ EXPOSE 7860                          │
│ CMD ["uvicorn", "server:app", ...]   │
└──────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│    Docker Image                      │
│    meta-data-cleaning:latest         │
└──────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│    Running Container                 │
│    - Port 7860 mapped                │
│    - Env vars set                    │
│    - Volume mounted (optional)       │
└──────────────────────────────────────┘
```

### Docker Compose Orchestration

```yaml
services:
  data-cleaning:      # Service 1
    build: ./env_a
    ports: [7860:7860]
    depends_on: []
    networks: [meta-network]
    
  code-review:        # Service 2
    build: ./env_b
    ports: [7861:7860]
    depends_on: []
    networks: [meta-network]
    
  interface:          # Service 3
    build: .
    ports: [7862:7860]
    depends_on:
      - data-cleaning
      - code-review
    networks: [meta-network]
    environment:
      DATA_CLEANING_API: http://data-cleaning:7860
      CODE_REVIEW_API: http://code-review:7860

networks:
  meta-network:       # Service communication
    driver: bridge
```

---

## 🎛️ Gradio Interface

### Component Structure

```
┌─────────────────────────────────────┐
│         Gradio Interface            │
├─────────────────────────────────────┤
│  ┌──────────────────────────────┐   │
│  │  Tab: Data Cleaning          │   │
│  │  ├─ Task Selector            │   │
│  │  ├─ Reset Button             │   │
│  │  ├─ Instruction Display      │   │
│  │  ├─ Dirty CSV Input          │   │
│  │  ├─ Schema Display           │   │
│  │  ├─ Solution Input           │   │
│  │  ├─ Submit Button            │   │
│  │  └─ Result Display           │   │
│  └──────────────────────────────┘   │
│                                     │
│  ┌──────────────────────────────┐   │
│  │  Tab: Code Review            │   │
│  │  ├─ Task Selector            │   │
│  │  ├─ Reset Button             │   │
│  │  ├─ Instruction Display      │   │
│  │  ├─ Code Display             │   │
│  │  ├─ Response Input (JSON)    │   │
│  │  ├─ Submit Button            │   │
│  │  └─ Result Display           │   │
│  └──────────────────────────────┘   │
│                                     │
│  ┌──────────────────────────────┐   │
│  │  Tab: Information            │   │
│  │  (Static documentation)      │   │
│  └──────────────────────────────┘   │
└─────────────────────────────────────┘
```

### Interface Flow

```
┌────────────────────┐
│  User Opens URL    │
└────────┬───────────┘
         │
         ▼
┌────────────────────┐
│  Gradio Loads      │
│  (HTML/JS/CSS)     │
└────────┬───────────┘
         │
         ▼
┌────────────────────┐
│  User Selects Tab  │
│  + Task            │
└────────┬───────────┘
         │
         ▼
┌────────────────────┐
│  Click Reset       │
│  → API /reset      │
└────────┬───────────┘
         │
         ▼
┌────────────────────┐
│  Display Problem   │
│  (CSV/Code)        │
└────────┬───────────┘
         │
         ▼
┌────────────────────┐
│  User Input Answer │
└────────┬───────────┘
         │
         ▼
┌────────────────────┐
│  Click Submit      │
│  → API /step       │
└────────┬───────────┘
         │
         ▼
┌────────────────────┐
│  Display Results   │
│  (Reward, Status)  │
└────────────────────┘
```

---

## 🔐 Security Considerations

### API Security

1. **Input Validation**
   - Pydantic models validate all inputs
   - Type checking on all fields
   - Size limits on data

2. **Error Handling**
   - Try-catch blocks around graders
   - Graceful error responses
   - No stack traces in responses

3. **Resource Limits**
   - Timeout on all operations
   - Memory limits in containers
   - Request size limits

### Data Sensitivity

- No sensitive data in logs
- Environment variables for credentials
- No raw responses exposed
- Clean error messages

---

## 📈 Performance Optimization

### Caching

```python
# Task configuration caching
@lru_cache(maxsize=10)
def get_task_config(task_name: str):
    return TASKS[task_name]

# Grader caching
self.graders = {
    "null_filling": NullFillingGrader(),  # Instantiated once
    ...
}
```

### Parallelization

- Multiple environment instances possible
- Stateless design allows horizontal scaling
- Docker Compose supports multiple replicas

### Monitoring

```python
def log_step(step: int, action: str, reward: float, 
             done: bool, error: Optional[str]):
    """Standardized logging for monitoring"""
    print(f"[STEP] step={step} action={action} reward={reward:.2f}")
```

---

## 📚 Key Design Patterns

### Factory Pattern

```python
# Grader selection
graders = {
    "null_filling": NullFillingGrader(),
    "type_coercion_dedup": TypeCoercionGrader(),
    "full_qa_pipeline": FullQAPipelineGrader(),
}
grader = graders[task_id]
```

### Strategy Pattern

```python
# Data generation strategies
if task_id == "null_filling":
    return _generate_null_filling_data(config)
elif task_id == "type_coercion_dedup":
    return _generate_type_coercion_data(config)
```

### Dependency Injection

```python
# FastAPI dependency injection (optional)
async def get_environment():
    return env

@app.post("/reset")
def reset(request, env = Depends(get_environment)):
    return env.reset(request.task_name)
```

---

## 🔄 State Management

### Single-Episode Design

- Each reset initializes fresh state
- Step() completes the episode
- No multi-step interactions
- Simplifies state tracking

### State Structure

```python
{
    "task_config": {...},      # Task metadata
    "step_count": int,         # Steps taken
    "episode_done": bool,      # Completion flag
    "dirty_data": DataFrame,   # Current input (reset only)
    "clean_data": DataFrame,   # Ground truth (hidden)
}
```

---

## 📊 Metrics & Evaluation

### Tracked Metrics

1. **Reward Score**: 0.0-1.0 per task
2. **Success Rate**: % of tasks passing (reward ≥ 0.5)
3. **Execution Time**: Seconds per task
4. **Error Rate**: % of failed submissions

### Baseline Benchmarks

```python
BASELINES = {
    "gpt-4": {
        "null_filling": 0.82,
        "type_coercion_dedup": 0.71,
        "full_qa_pipeline": 0.58,
        "bug_detection": 0.88,
        "security_review": 0.75,
        "full_pr_review": 0.62,
    }
}
```

---

## 🚀 Deployment Topology

### Development
```
Local Machine
├── env_a (terminal 1)
├── env_b (terminal 2)
└── interface (terminal 3)
```

### Production (Docker Compose)
```
Single Host
├── Container: data-cleaning
├── Container: code-review
├── Container: interface
└── Network: meta-network
```

### HF Spaces
```
HF Infrastructure
├── Docker Container
├── Auto-scaling
├── Public Access
└── GPU Support (optional)
```

---

## 📖 References

- [OpenEnv Specification](https://github.com/allenai/openenv)
- [FastAPI Best Practices](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Docker Compose Guide](https://docs.docker.com/compose/)
- [Gradio Docs](https://www.gradio.app/)
