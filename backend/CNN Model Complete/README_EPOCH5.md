# Running the Epoch 5 Model

This guide will help you run the trained CNN model from epoch 5 for text classification.

## Model Information
- **Model File**: `models/model__epoch_5_maxlen_1500_lr_0.0025_loss_0.2753_acc_0.8766_f1_0.875.pth`
- **Accuracy**: 87.66%
- **F1 Score**: 87.5%
- **Loss**: 0.2753
- **Max Length**: 1500 characters

## Quick Start

### Option 1: Using the Batch File (Windows)
```cmd
run_epoch5.bat "Your text to classify here"
```

### Option 2: Using PowerShell
```powershell
.\run_epoch5.ps1 -Text "Your text to classify here"
```

### Option 3: Direct Python Command
```cmd
python character-based-cnn-master\predict.py --model "models\model__epoch_5_maxlen_1500_lr_0.0025_loss_0.2753_acc_0.8766_f1_0.875.pth" --text "Your text here" --max_length 1500
```

## Fixing PyTorch Installation Issues

If you encounter PyTorch import errors, you may need to enable Windows Long Path support:

### Method 1: Enable Long Paths via Registry
1. Open Registry Editor (regedit) as Administrator
2. Navigate to: `HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\FileSystem`
3. Set `LongPathsEnabled` to `1`
4. Restart your computer

### Method 2: Enable via Group Policy
1. Open Group Policy Editor (gpedit.msc) as Administrator
2. Navigate to: Computer Configuration > Administrative Templates > System > Filesystem
3. Enable "Enable Win32 long paths"
4. Restart your computer

### Method 3: Alternative PyTorch Installation
Try installing PyTorch in a shorter path:
```cmd
# Create a new virtual environment in a shorter path
python -m venv C:\temp\cnn_env
C:\temp\cnn_env\Scripts\activate
pip install torch torchvision torchaudio
```

## Example Usage

### Human-written text example:
```cmd
run_epoch5.bat "I absolutely love this movie! The cinematography is breathtaking and the story really touched my heart. The actors delivered outstanding performances."
```

### AI-generated text example:
```cmd
run_epoch5.bat "This product demonstrates exceptional quality and performance characteristics. The implementation utilizes advanced methodologies to achieve optimal results."
```

## Understanding the Output

The model outputs probabilities for two classes:
- **[Human, AI]**: `[0.8234, 0.1766]`
  - 82.34% probability the text is human-written
  - 17.66% probability the text is AI-generated

## Model Architecture

The model uses a Character-level CNN with:
- Input: Character sequences (max 1500 characters)
- Alphabet: 69 characters (lowercase letters, numbers, punctuation)
- Convolutional layers: 6 layers with varying filter sizes
- Fully connected layers: 2 layers (1024 neurons each)
- Output: Binary classification (Human vs AI)

## Troubleshooting

1. **Import Error**: Ensure PyTorch is properly installed
2. **Model Not Found**: Check that the model file exists in the `models/` directory
3. **CUDA Error**: The model will automatically use CPU if CUDA is not available
4. **Path Issues**: Use absolute paths if relative paths don't work

## Files Created
- `run_epoch5.bat` - Windows batch file for easy execution
- `run_epoch5.ps1` - PowerShell script for execution
- `run_epoch5_model.py` - Python script with enhanced features (requires working PyTorch)