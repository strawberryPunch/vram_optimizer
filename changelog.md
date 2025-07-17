# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-18

### Added
- Initial release of StrawberryFist VRAM Optimizer
- **StFist - VRAM Optimizer** node with the following features:
  - Automatic VRAM cleanup after queue execution
  - Multiple cleaning modes (Standard/Aggressive)
  - Smart cleaning conditions (Every Time/Only When High)
  - Flexible timing options (Before Queue/After Queue/Both)
  - Manual trigger functionality
  - Real-time terminal logging
  - ComfyUI queue execution hooks
  - Automatic dependency installation

- **StFist - GPU Monitor** node with the following features:
  - Real-time GPU memory monitoring
  - Background monitoring thread
  - Historical data tracking
  - Warning system with customizable thresholds
  - Visual memory usage bars with color coding
  - Trend analysis (increasing/decreasing/stable)
  - Multiple output parameters for workflow integration
  - Configurable update intervals and history length

### Technical Features
- Modular architecture with separate utility modules
- Singleton pattern for instance management
- Thread-safe background monitoring
- Comprehensive error handling
- Automatic GPU detection and fallback systems
- ComfyUI cache prevention mechanisms

### Dependencies
- GPUtil >= 1.4.0 (automatically installed)
- PyTorch (existing ComfyUI dependency)
- Python 3.8+ support

### Documentation
- Comprehensive README with usage examples
- Visual ASCII art status displays
- Detailed configuration options
- Installation instructions for multiple methods
- Troubleshooting guide

## [Unreleased]

### Planned Features
- Memory usage graphs and charts
- Export monitoring data to CSV/JSON
- Email/Discord notifications for critical memory usage
- Integration with other ComfyUI performance tools
- Custom memory cleaning strategies
- Multi-GPU support
- Memory usage predictions and recommendations

---

## Release Notes

### v1.0.0 - Initial Release
This is the first stable release of the StrawberryFist VRAM Optimizer. The package provides a complete solution for VRAM management in ComfyUI with both automated cleanup and real-time monitoring capabilities.

Key highlights:
- 🚀 **Zero-configuration setup** - Works out of the box
- 🎯 **Intelligent cleaning** - Only cleans when needed
- 📊 **Real-time monitoring** - Always know your GPU status
- 🔧 **Highly configurable** - Adapt to your workflow
- 🍓 **Beautiful UI** - ASCII art status displays

The project is ready for production use and has been tested with various ComfyUI workflows and GPU configurations.