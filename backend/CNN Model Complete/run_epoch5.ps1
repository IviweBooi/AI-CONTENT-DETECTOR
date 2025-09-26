param(
    [string]$Text = "I love this movie! It's absolutely fantastic and well-written."
)

Write-Host "Running Epoch 5 Model..." -ForegroundColor Green
Write-Host ""

# Set the model path
$ModelPath = "models\model__epoch_5_maxlen_1500_lr_0.0025_loss_0.2753_acc_0.8766_f1_0.875.pth"

Write-Host "Input text: $Text" -ForegroundColor Yellow
Write-Host "Model: $ModelPath" -ForegroundColor Yellow
Write-Host ""

# Activate virtual environment and run the prediction
& "venv\Scripts\Activate.ps1"
python "character-based-cnn-master\predict.py" --model $ModelPath --text $Text --max_length 1500

Write-Host ""
Write-Host "Done!" -ForegroundColor Green