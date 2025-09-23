# Daily Incremental Training Guide

## Overview
This guide explains how to use the incremental training system to train your AI content detector model in manageable daily chunks instead of processing the entire dataset at once.

## Quick Start

### 1. Run Daily Training Session
```bash
python incremental_fine_tuning.py --chunk-size 2000 --max-chunks 1
```

### 2. Test Model Performance
```bash
python test_incremental_model.py
```

## Training Parameters

### Chunk Size
- **Default**: 2000 samples per chunk
- **Recommended**: 1000-3000 samples for daily training
- **Adjust based on**: Available time and computational resources

### Max Chunks
- **Default**: 1 chunk per session
- **For longer sessions**: Increase to 2-3 chunks
- **For quick updates**: Keep at 1 chunk

## Training Schedule Recommendations

### Daily Training (Recommended)
```bash
# Monday - Friday: Regular training
python incremental_fine_tuning.py --chunk-size 2000 --max-chunks 1

# Weekend: Longer sessions if needed
python incremental_fine_tuning.py --chunk-size 2000 --max-chunks 2
```

### Weekly Training
```bash
# Once per week: Larger chunks
python incremental_fine_tuning.py --chunk-size 5000 --max-chunks 2
```

## Monitoring Progress

### Check Training History
The training history is automatically saved in:
```
incremental_checkpoints/training_history.json
```

### Model Checkpoints
Models are saved after each chunk in:
```
incremental_checkpoints/model_after_chunk_X/
```

### Performance Testing
Run performance tests regularly:
```bash
python test_incremental_model.py
```

## Key Features

### Automatic Checkpointing
- Models are automatically saved after each training chunk
- Training can be resumed from the latest checkpoint
- No data loss if training is interrupted

### Class Balancing
- Automatic class weight calculation for balanced training
- Handles imbalanced datasets effectively

### Memory Efficient
- Processes data in small chunks
- Suitable for systems with limited memory
- Prevents out-of-memory errors

## Troubleshooting

### Common Issues

1. **"Could not find platform independent libraries" Warning**
   - This is a harmless Python environment warning
   - Training will continue normally

2. **Out of Memory Errors**
   - Reduce `chunk_size` (try 1000 or 1500)
   - Reduce `per_device_train_batch_size` in the script

3. **Training Too Slow**
   - Increase `chunk_size` if you have more memory
   - Reduce `num_train_epochs` for faster training

### Performance Monitoring

Monitor these metrics after each training session:
- **Accuracy**: Should gradually improve
- **F1 Score**: Balanced measure of precision and recall
- **Training Loss**: Should decrease over time

## Dataset Information

- **Total Samples**: 28,662 (50% human, 50% AI)
- **Average Text Length**: 1,373 characters
- **Chunk Coverage**: Each 2000-sample chunk covers ~7% of total dataset
- **Complete Training**: Approximately 14-15 daily sessions

## Best Practices

1. **Consistent Schedule**: Train regularly for best results
2. **Monitor Performance**: Test model after every few training sessions
3. **Backup Checkpoints**: Keep copies of important model checkpoints
4. **Track Progress**: Review training history regularly
5. **Adjust Parameters**: Modify chunk size based on available time

## Example Training Session

```bash
# Day 1: Start training
python incremental_fine_tuning.py --chunk-size 2000 --max-chunks 1

# Test performance
python test_incremental_model.py

# Day 2: Continue training (automatic checkpoint loading)
python incremental_fine_tuning.py --chunk-size 2000 --max-chunks 1

# Day 3: Continue training
python incremental_fine_tuning.py --chunk-size 2000 --max-chunks 1

# ... continue daily until dataset is complete
```

## Advanced Usage

### Custom Chunk Sizes
```bash
# Small chunks for quick daily updates
python incremental_fine_tuning.py --chunk-size 1000 --max-chunks 1

# Large chunks for weekend training
python incremental_fine_tuning.py --chunk-size 4000 --max-chunks 2
```

### Multiple Chunks per Session
```bash
# Train multiple chunks in one session
python incremental_fine_tuning.py --chunk-size 2000 --max-chunks 3
```

This approach allows you to gradually improve your model's performance while maintaining a manageable training schedule that fits your daily routine.