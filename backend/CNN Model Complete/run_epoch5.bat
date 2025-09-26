@echo off
echo Running Epoch 5 Model...
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Set the model path
set MODEL_PATH=models\model__epoch_5_maxlen_1500_lr_0.0025_loss_0.2753_acc_0.8766_f1_0.875.pth

REM Check if text argument is provided
if "%~1"=="" (
    echo Usage: run_epoch5.bat "Your text here"
    echo Example: run_epoch5.bat "This is a sample text to classify"
    echo.
    echo Using default text...
    set TEXT=I love this movie! It's absolutely fantastic and well-written.
) else (
    set TEXT=%~1
)

echo Input text: %TEXT%
echo Model: %MODEL_PATH%
echo.

REM Run the prediction
python character-based-cnn-master\predict.py --model "%MODEL_PATH%" --text "%TEXT%" --max_length 1500

echo.
echo Done!
pause