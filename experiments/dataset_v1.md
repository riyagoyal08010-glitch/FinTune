# FinQA Dataset v1

## Dataset Summary

FinTune uses the FinQA dataset as the primary numerical
financial reasoning dataset.

After preprocessing and duplicate removal:

- Training examples: 6,200
- Development examples: 876
- Total: 7,076

## Preprocessing

The preprocessing pipeline performs:

1. Question normalization
2. Missing-answer recovery using the final reasoning step
3. Gold evidence extraction
4. Program extraction
5. Empty-example filtering
6. Exact duplicate removal
7. Train/dev exact-example leakage removal
8. Dataset validation

## Training Distribution

### Question Length

- Average: 16.65 words
- Minimum: 5 words
- Maximum: 62 words

### Answer Types

- Percentage: 56.42%
- Numeric: 39.55%
- Other: 2.03%
- Yes/No: 2.00%

### Evidence

- Average evidence items: 1.70
- Maximum evidence items: 9
- Average evidence length: 61.82 words
- Maximum evidence length: 289 words

### Program Complexity

- Average operations/example: 1.53
- Maximum operations/example: 6

### Operations

- Divide: 46.42%
- Subtract: 28.49%
- Add: 15.69%
- Multiply: 5.87%
- Greater: 1.30%
- Table average: 1.00%
- Table max: 0.51%
- Table sum: 0.38%
- Table min: 0.28%
- Exp: 0.05%

### Operations Per Example

- 1 operation: 59.56%
- 2 operations: 32.24%
- 3 operations: 5.16%
- 4 operations: 1.50%
- 5 operations: 1.44%
- 6 operations: 0.10%

## Development Distribution

- Examples: 876
- Average question length: 16.42 words
- Average evidence items: 1.71
- Average evidence length: 61.87 words
- Average operations/example: 1.54

## Leakage Handling

Exact example duplicates were identified using:

question + evidence + program + answer

rather than question alone.

This is important because identical question wording can occur
with different financial contexts.

Exact duplicate examples were removed from the training and
development datasets, and exact train/dev example duplicates
were removed from training.

## Dataset Status

FinQA preprocessing and auditing are complete.

This version is frozen for the initial FinTune experiments.