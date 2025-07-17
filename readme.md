# 🍓 StrawberryFist VRAM Optimizer for ComfyUI

![Version](https://img.shields.io/badge/version-1.0.0-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blue)
![ComfyUI](https://img.shields.io/badge/ComfyUI-Compatible-orange)

A comprehensive VRAM management solution for ComfyUI that automatically optimizes GPU memory usage and provides real-time monitoring.

## 🎯 Features

### 🔧 VRAM Optimizer
- **Automatic VRAM cleanup** after each queue execution
- **Multiple cleaning modes**: Standard and Aggressive
- **Smart cleaning conditions**: Clean every time or only when memory usage is high
- **Flexible timing**: Clean before queue, after queue, or both
- **Manual trigger**: Force cleanup with a simple parameter change
- **Real-time logging**: Monitor all activities in the terminal

### 📊 GPU Monitor
- **Real-time GPU monitoring** with background thread
- **Memory usage visualization** with color-coded progress bars
- **Historical data tracking** with configurable history length
- **Warning system** with customizable thresholds
- **Trend analysis** showing memory usage patterns
- **Multiple outputs** for integration with other nodes

## 🚀 Installation

### Method 1: ComfyUI Manager (Recommended)
1. Open ComfyUI Manager
2. Search for "StrawberryFist VRAM Optimizer"
3. Click Install
4. Restart ComfyUI

### Method 2: Manual Installation
1. Navigate to your ComfyUI custom nodes directory:
   ```
   cd ComfyUI/custom_nodes/
   ```
2. Clone this repository:
   ```
   git clone https://github.com/YourUsername/comfyui-strawberryfist-vram-optimizer.git
   ```
3. Restart ComfyUI

### Method 3: Download ZIP
1. Download the latest release from [Releases](https://github.com/YourUsername/comfyui-strawberryfist-vram-optimizer/releases)
2. Extract to `ComfyUI/custom_nodes/`
3. Restart ComfyUI

## 📋 Requirements

- ComfyUI
- Python 3.8+
- PyTorch with CUDA support
- GPUtil (automatically installed)

## 🎮 Usage

### VRAM Optimizer Node

1. Add the **StFist - VRAM Optimizer** node to your workflow
2. Configure the settings:
   - **enabled**: Turn automatic cleaning on/off
   - **clear_mode**: Choose between Standard or Aggressive cleaning
   - **auto_clean**: Set cleaning conditions (Every Time or Only When High)
   - **run_timing**: Choose when to clean (After Queue, Before Queue, or Both)
   - **force_run**: Change this value to manually trigger cleaning

### GPU Monitor Node

1. Add the **StFist - GPU Monitor** node to your workflow
2. Configure the monitoring settings:
   - **monitoring_enabled**: Turn real-time monitoring on/off
   - **update_interval**: Set monitoring frequency (0.1-10 seconds)
   - **history_length**: Number of data points to keep (10-300)
   - **warning_threshold**: Memory usage warning level (50-95%)
   - **refresh_trigger**: Change to force immediate update

## 📸 Screenshots

### VRAM Optimizer in Action
```
🎮 ═══════════════════════════════════════════════════════════
🔥 StrawberryFist VRAM Optimizer v3.0 [14:23:45]
🔄 실행 횟수: 5 | 상태: CLEANED_1024.3MB
⚙️ 설정: After Queue / Standard
═══════════════════════════════════════════════════════════

📊 GPU 메모리 상태 (NVIDIA GeForce RTX 4090)
┌─────────────────────────────────────────────────────────┐
│ ✅ 사용률: 15.2% (GOOD)                                  │
│ 📈 사용량: 3724.1MB / 24564.0MB                         │
│ 🟢🟢🟢🟢⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜ │
└─────────────────────────────────────────────────────────┘
```

### GPU Monitor Dashboard
```
🎮 ═══════════════════════════════════════════════════════════
🔥 StrawberryFist GPU 실시간 모니터링 [14:23:45]
═══════════════════════════════════════════════════════════

📊 GPU: NVIDIA GeForce RTX 4090
┌─────────────────────────────────────────────────────────┐
│ ⚠️ 사용률: 75.3% (WARNING)                               │
│ 📈 사용량: 18500.2MB / 24564.0MB                        │
│ 🟡🟡🟡🟡🟡🟡🟡🟡🟡🟡🟡🟡🟡🟡🟡🟡🟡🟡🟡⬜⬜⬜⬜⬜⬜ │
└─────────────────────────────────────────────────────────┘

📈 최근 통계 (최근 10개 샘플)
┌─────────────────────────────────────────────────────────┐
│ 평균: 72.5% | 최대: 89.1% | 최소: 65.2%                  │
│ 경고 임계값: 80.0%                                       │
└─────────────────────────────────────────────────────────┘

📊 트렌드: 📈 증가 추세
```

## ⚙️ Configuration

### VRAM Optimizer Settings

| Parameter | Options | Default | Description |
|-----------|---------|---------|-------------|
| enabled | On/Off | On | Enable/disable automatic VRAM cleaning |
| clear_mode | Standard/Aggressive | Standard | Cleaning intensity level |
| auto_clean | Every Time/Only When High | Every Time | Cleaning trigger condition |
| run_timing | After Queue/Before Queue/Both | After Queue | When to perform cleaning |
| force_run | 0-999 | 0 | Manual trigger (change value to execute) |

### GPU Monitor Settings

| Parameter | Range | Default | Description |
|-----------|-------|---------|-------------|
| monitoring_enabled | On/Off | On | Enable/disable real-time monitoring |
| update_interval | 0.1-10.0 | 1.0 | Update frequency in seconds |
| history_length | 10-300 | 60 | Number of data points to keep |
| warning_threshold | 50.0-95.0 | 80.0 | Memory usage warning percentage |
| refresh_trigger | 0-9999 | 0 | Manual refresh trigger |

## 🔧 Advanced Features

### Automatic Dependency Installation
The nodes automatically install required dependencies (GPUtil) on first run.

### Background Monitoring
The GPU Monitor runs in a separate thread to provide real-time data without blocking ComfyUI.

### ComfyUI Integration
Automatically hooks into ComfyUI's queue execution system for seamless VRAM management.

### Terminal Logging
Comprehensive logging system provides detailed information about all operations.

## 🐛 Troubleshooting

### Common Issues

1. **"GPU not found" error**
   - Ensure GPUtil is installed: `pip install GPUtil`
   - Check if your GPU is properly detected by your system

2. **VRAM cleaning not working**
   - Verify PyTorch CUDA support: `torch.cuda.is_available()`
   - Check if CUDA drivers are properly installed

3. **Monitoring not updating**
   - Increase the update interval
   - Check ComfyUI terminal for error messages

### Getting Help

If you encounter issues:
1. Check the ComfyUI terminal for error messages
2. Open an issue on GitHub with detailed information
3. Join our community discussions

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- ComfyUI team for the amazing framework
- GPUtil library for GPU monitoring capabilities
- Community feedback and suggestions

## 🔗 Links

- [ComfyUI](https://github.com/comfyanonymous/ComfyUI)
- [ComfyUI Manager](https://github.com/ltdrdata/ComfyUI-Manager)
- [Report Issues](https://github.com/YourUsername/comfyui-strawberryfist-vram-optimizer/issues)

---

Made with ❤️ by StrawberryFist | 🍓 Optimizing your ComfyUI experience!