import time
import threading

# Automatic dependency installation
try:
    from .utils import install_from_requirements
    install_from_requirements()
    print("🍓 [StrawberryFist] All dependencies loaded successfully!")
except Exception as e:
    print(f"🍓 [StrawberryFist] Error occurred during dependency installation: {e}")

# Import required modules
from .utils import GPUMonitor, VRAMCleaner
from .hooks import ComfyUIHooks

class StrawberryVramOptimizer:
    """StrawberryFist VRAM Optimization Node"""
    
    _instance = None
    _is_initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._is_initialized:
            self.settings = {
                'enabled': True,
                'clear_mode': 'Standard',
                'auto_clean': 'Every Time',
                'run_timing': 'After Queue'
            }
            self.last_execution_time = 0
            self.execution_count = 0
            self.last_force_run = 0
            self._is_initialized = True
            
            # Initialize components
            self.gpu_monitor = GPUMonitor()
            self.vram_cleaner = VRAMCleaner()
            self.hooks = ComfyUIHooks(self)
            
            # Try to register hooks immediately
            self.hooks.try_register_hooks()
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "enabled": (
                    ["On", "Off"],
                    {
                        "default": "On",
                        "tooltip": "Created by: StrawberryFist\n\nAutomatically clears VRAM after each queue execution.\nExecutes 'torch.cuda.empty_cache()'"
                    }
                ),
                "clear_mode": (
                    ["Standard", "Aggressive"],
                    {
                        "default": "Standard",
                        "tooltip": "Standard: Basic VRAM cleanup\nAggressive: Additional memory cleanup included"
                    }
                ),
                "auto_clean": (
                    ["Every Time", "Only When High"],
                    {
                        "default": "Every Time",
                        "tooltip": "Every Time: Execute every time\nOnly When High: Execute only when VRAM usage is 70% or higher"
                    }
                ),
                "run_timing": (
                    ["After Queue", "Before Queue", "Both"],
                    {
                        "default": "After Queue",
                        "tooltip": "After Queue: Clean after queue execution\nBefore Queue: Clean before queue execution\nBoth: Clean before and after execution"
                    }
                ),
                "force_run": (
                    "INT",
                    {
                        "default": 0,
                        "min": 0,
                        "max": 999,
                        "step": 1,
                        "tooltip": "Change this value to manually trigger VRAM cleanup"
                    }
                )
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("status",)
    FUNCTION = "setup_and_run"
    OUTPUT_NODE = True
    CATEGORY = "StrawberryFist - system"
    
    @classmethod
    def IS_CHANGED(cls, **kwargs):
        # Always return different value to prevent caching
        return time.time()
    
    def setup_and_run(self, enabled, clear_mode, auto_clean, run_timing, force_run):
        current_time = time.strftime("%H:%M:%S", time.localtime())
        
        # Detect setting changes
        old_settings = self.settings.copy()
        new_settings = {
            'enabled': enabled == "On",
            'clear_mode': clear_mode,
            'auto_clean': auto_clean,
            'run_timing': run_timing
        }
        
        # Check if settings have changed
        settings_changed = (old_settings != new_settings)
        force_run_changed = (force_run != self.last_force_run)
        
        # Log changes
        if settings_changed:
            print(f"\n⚙️ [{current_time}] === Settings Change Detected ===")
            for key, value in new_settings.items():
                if old_settings.get(key) != value:
                    print(f"   📝 {key}: {old_settings.get(key)} → {value}")
            print(f"⚙️ [{current_time}] === Settings Change Completed ===\n")
        
        # Update settings
        self.settings.update(new_settings)
        self.last_force_run = force_run
        
        # Update VRAM cleaner mode
        self.vram_cleaner.clear_mode = clear_mode
        
        # Try to register hooks when settings change
        if settings_changed:
            self.hooks.try_register_hooks()
        
        # Check execution conditions
        should_run = False
        run_reason = ""
        
        if force_run_changed and force_run > 0:
            should_run = True
            run_reason = f"Manual execution (trigger: {force_run})"
        elif settings_changed:
            should_run = True
            run_reason = "Auto execution after settings change"
        elif self.execution_count == 0:
            should_run = True
            run_reason = "Initial execution"
        
        # Execute or check status
        if should_run:
            if force_run_changed and force_run > 0:
                print(f"\n🔧 [{current_time}] === Manual VRAM Cleanup Execution (trigger: {force_run}) ===")
            elif settings_changed:
                print(f"\n🔧 [{current_time}] === VRAM Cleanup Execution After Settings Change ===")
            
            result = self.perform_vram_cleanup(force_run=True, reason=run_reason)
            
            if force_run_changed and force_run > 0:
                print(f"🔧 [{current_time}] === Manual VRAM Cleanup Completed ===\n")
            elif settings_changed:
                print(f"🔧 [{current_time}] === VRAM Cleanup After Settings Change Completed ===\n")
        else:
            # Simple status check without setting changes
            result = self.get_current_status()
        
        return result
    
    def perform_vram_cleanup(self, force_run=False, reason="Auto execution"):
        """Execute VRAM cleanup"""
        try:
            current_time = time.strftime("%H:%M:%S", time.localtime())
            self.execution_count += 1
            
            # Execution log
            print(f"🎯 [{current_time}] VRAM cleanup started - {reason} (execution count: {self.execution_count})")
            
            # Check if disabled
            if not self.settings['enabled'] and not force_run:
                disabled_msg = f"⏸️ [Execution#{self.execution_count}] [{current_time}] VRAM cleanup disabled"
                print(disabled_msg)
                return {
                    "ui": {"text": disabled_msg},
                    "result": (disabled_msg,)
                }
            
            # Check GPU information
            gpu_info = self.gpu_monitor.get_gpu_info()
            if not gpu_info:
                error_msg = f"❌ [Execution#{self.execution_count}] [{current_time}] GPU not found"
                print(error_msg)
                return {
                    "ui": {"text": error_msg},
                    "result": (error_msg,)
                }
            
            # Log GPU status
            self.gpu_monitor.log_gpu_status(self.execution_count)
            
            # Check cleanup execution conditions
            should_clean = self.settings['enabled'] or force_run
            if should_clean and not self.gpu_monitor.should_clean_memory(self.settings['auto_clean']):
                should_clean = False
                skip_msg = f"ℹ️ [Execution#{self.execution_count}] [{current_time}] VRAM usage {gpu_info['percent']:.1f}% < 70% → Cleanup skipped"
                print(skip_msg)
                return {
                    "ui": {"text": skip_msg},
                    "result": (skip_msg,)
                }
            
            # Execute VRAM cleanup
            if should_clean:
                # Progress log
                self.vram_cleaner.log_cleanup_progress(current_time)
                
                # Execute cleanup
                cleanup_result = self.vram_cleaner.perform_cleanup()
                
                # Result log
                self.vram_cleaner.log_cleanup_result(cleanup_result, current_time)
                
                # Generate UI message
                ui_message = self.vram_cleaner.generate_ui_message(cleanup_result, current_time, self.execution_count)
                
                # Final status log
                final_status = "CLEANED" if cleanup_result['success'] and cleanup_result['cleared'] > 0 else "ALREADY_CLEAN"
                print(f"🍓 [{current_time}] Final status: {final_status}")
                
                return {
                    "ui": {"text": ui_message},
                    "result": (ui_message,)
                }
            
            # Disabled state
            disabled_msg = f"⏸️ [Execution#{self.execution_count}] [{current_time}] VRAM cleanup disabled"
            return {
                "ui": {"text": disabled_msg},
                "result": (disabled_msg,)
            }
            
        except Exception as e:
            current_time = time.strftime("%H:%M:%S", time.localtime())
            error_msg = f"💥 [Execution#{self.execution_count}] [{current_time}] VRAM cleanup error: {str(e)}"
            print(f"💥 [{current_time}] VRAM cleanup error: {str(e)}")
            return {
                "ui": {"text": error_msg},
                "result": (error_msg,)
            }
    
    def get_current_status(self):
        """Check current status only (without executing cleanup)"""
        try:
            current_time = time.strftime("%H:%M:%S", time.localtime())
            
            # Check GPU information
            gpu_info = self.gpu_monitor.get_gpu_info()
            if not gpu_info:
                error_msg = f"❌ [Check#{self.execution_count}] [{current_time}] GPU not found"
                return {
                    "ui": {"text": error_msg},
                    "result": (error_msg,)
                }
            
            # Current status log
            print(f"📊 [{current_time}] Current status check - GPU usage: {gpu_info['percent']:.1f}%")
            
            status_msg = f"📊 [Check#{self.execution_count}] [{current_time}] Current status - GPU usage: {gpu_info['percent']:.1f}%"
            return {
                "ui": {"text": status_msg},
                "result": (status_msg,)
            }
            
        except Exception as e:
            current_time = time.strftime("%H:%M:%S", time.localtime())
            error_msg = f"💥 [Check#{self.execution_count}] [{current_time}] Status check error: {str(e)}"
            return {
                "ui": {"text": error_msg},
                "result": (error_msg,)
            }


class StrawberryGPUMonitor:
    """Real-time GPU Monitoring Node"""
    
    _instance = None
    _monitor_thread = None
    _is_monitoring = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self.gpu_monitor = GPUMonitor()
            self.monitor_data = {
                'current_percent': 0,
                'current_used': 0,
                'current_total': 0,
                'gpu_name': 'Unknown',
                'last_update': time.time(),
                'history': []
            }
            self._initialized = True
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "monitoring_enabled": (
                    ["On", "Off"],
                    {
                        "default": "On",
                        "tooltip": "Enable/disable real-time GPU monitoring"
                    }
                ),
                "update_interval": (
                    "FLOAT",
                    {
                        "default": 1.0,
                        "min": 0.1,
                        "max": 10.0,
                        "step": 0.1,
                        "tooltip": "Monitoring update interval (seconds)"
                    }
                ),
                "history_length": (
                    "INT",
                    {
                        "default": 60,
                        "min": 10,
                        "max": 300,
                        "step": 1,
                        "tooltip": "Number of history entries to keep"
                    }
                ),
                "warning_threshold": (
                    "FLOAT",
                    {
                        "default": 80.0,
                        "min": 50.0,
                        "max": 95.0,
                        "step": 5.0,
                        "tooltip": "Warning threshold (%)"
                    }
                ),
                "refresh_trigger": (
                    "INT",
                    {
                        "default": 0,
                        "min": 0,
                        "max": 9999,
                        "step": 1,
                        "tooltip": "Change value to trigger immediate update"
                    }
                )
            }
        }
    
    RETURN_TYPES = ("STRING", "FLOAT", "FLOAT", "FLOAT", "STRING")
    RETURN_NAMES = ("status", "usage_percent", "used_mb", "total_mb", "gpu_name")
    FUNCTION = "monitor_gpu"
    OUTPUT_NODE = True
    CATEGORY = "StrawberryFist - system"
    
    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return time.time()
    
    def start_monitoring(self, update_interval, history_length, warning_threshold):
        """Start background monitoring"""
        if self._is_monitoring:
            return
        
        self._is_monitoring = True
        
        def monitor_loop():
            while self._is_monitoring:
                try:
                    gpu_info = self.gpu_monitor.get_gpu_info()
                    current_time = time.time()
                    
                    if gpu_info:
                        self.monitor_data.update({
                            'current_percent': gpu_info['percent'],
                            'current_used': gpu_info['used'],
                            'current_total': gpu_info['total'],
                            'gpu_name': gpu_info['name'],
                            'last_update': current_time
                        })
                        
                        # Add to history
                        self.monitor_data['history'].append({
                            'time': current_time,
                            'percent': gpu_info['percent'],
                            'used': gpu_info['used']
                        })
                        
                        # Limit history length
                        if len(self.monitor_data['history']) > history_length:
                            self.monitor_data['history'].pop(0)
                        
                        # Check warnings
                        if gpu_info['percent'] > warning_threshold:
                            print(f"🚨 [GPU Warning] Memory usage: {gpu_info['percent']:.1f}% (threshold: {warning_threshold}%)")
                    
                    time.sleep(update_interval)
                except Exception as e:
                    print(f"🍓 [GPU Monitoring] Error: {e}")
                    time.sleep(update_interval)
        
        self._monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self._monitor_thread.start()
        print(f"🍓 [GPU Monitoring] Started - interval: {update_interval}s")
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        if self._is_monitoring:
            self._is_monitoring = False
            if self._monitor_thread:
                self._monitor_thread.join(timeout=1)
            print("🍓 [GPU Monitoring] Stopped")
    
    def generate_status_display(self, warning_threshold):
        """Generate status display"""
        data = self.monitor_data
        current_time = time.strftime("%H:%M:%S", time.localtime())
        
        # Generate memory bar
        bar_info = self.gpu_monitor.generate_memory_bar(data['current_percent'])
        
        # Generate status message
        status_lines = []
        status_lines.append(f"🎮 ═══════════════════════════════════════════════════════════")
        status_lines.append(f"🔥 StrawberryFist GPU Real-time Monitoring [{current_time}]")
        status_lines.append(f"═══════════════════════════════════════════════════════════")
        status_lines.append(f"")
        
        # GPU information
        status_lines.append(f"📊 GPU: {data['gpu_name']}")
        status_lines.append(f"┌─────────────────────────────────────────────────────────┐")
        status_lines.append(f"│ {bar_info['emoji']} Usage: {data['current_percent']:.1f}% ({bar_info['color']})                    │")
        status_lines.append(f"│ 📈 Memory: {data['current_used']:.1f}MB / {data['current_total']:.1f}MB                   │")
        status_lines.append(f"│ {bar_info['bar']} │")
        status_lines.append(f"└─────────────────────────────────────────────────────────┘")
        status_lines.append(f"")
        
        # History information
        if len(data['history']) > 1:
            recent_history = data['history'][-10:]  # Recent 10 entries
            avg_percent = sum(h['percent'] for h in recent_history) / len(recent_history)
            max_percent = max(h['percent'] for h in recent_history)
            min_percent = min(h['percent'] for h in recent_history)
            
            status_lines.append(f"📈 Recent Statistics (last {len(recent_history)} samples)")
            status_lines.append(f"┌─────────────────────────────────────────────────────────┐")
            status_lines.append(f"│ Average: {avg_percent:.1f}% | Max: {max_percent:.1f}% | Min: {min_percent:.1f}% │")
            status_lines.append(f"│ Warning threshold: {warning_threshold:.1f}%                          │")
            status_lines.append(f"└─────────────────────────────────────────────────────────┘")
            status_lines.append(f"")
        
        # Trend analysis
        if len(data['history']) >= 5:
            recent_5 = [h['percent'] for h in data['history'][-5:]]
            if recent_5[-1] > recent_5[0]:
                trend = "📈 Increasing trend"
            elif recent_5[-1] < recent_5[0]:
                trend = "📉 Decreasing trend"
            else:
                trend = "➡️ Stable"
            
            status_lines.append(f"📊 Trend: {trend}")
            status_lines.append(f"")
        
        # Warning message
        if data['current_percent'] > warning_threshold:
            status_lines.append(f"🚨 Warning: Memory usage exceeded threshold!")
            status_lines.append(f"")
        
        status_lines.append(f"🍓 Real-time monitoring active... 🍓")
        
        return "\n".join(status_lines)
    
    def monitor_gpu(self, monitoring_enabled, update_interval, history_length, warning_threshold, refresh_trigger):
        """GPU monitoring main function"""
        try:
            current_time = time.strftime("%H:%M:%S", time.localtime())
            
            # Control monitoring state
            if monitoring_enabled == "On":
                if not self._is_monitoring:
                    self.start_monitoring(update_interval, history_length, warning_threshold)
            else:
                if self._is_monitoring:
                    self.stop_monitoring()
                
                # Monitoring disabled message
                disabled_msg = f"⏸️ [{current_time}] GPU real-time monitoring disabled"
                return (
                    disabled_msg,
                    0.0,
                    0.0,
                    0.0,
                    "Unknown",
                    {"ui": {"text": disabled_msg}}
                )
            
            # Get current GPU information
            gpu_info = self.gpu_monitor.get_gpu_info()
            if not gpu_info:
                error_msg = f"❌ [{current_time}] Cannot get GPU information"
                return (
                    error_msg,
                    0.0,
                    0.0,
                    0.0,
                    "Error",
                    {"ui": {"text": error_msg}}
                )
            
            # Real-time log (optional)
            if refresh_trigger > 0:
                print(f"🔄 [{current_time}] GPU status update - usage: {gpu_info['percent']:.1f}%")
            
            # Generate status display
            status_display = self.generate_status_display(warning_threshold)
            
            # Simple status string
            status_text = f"GPU: {gpu_info['percent']:.1f}% ({gpu_info['used']:.1f}MB/{gpu_info['total']:.1f}MB)"
            
            return (
                status_text,
                gpu_info['percent'],
                gpu_info['used'],
                gpu_info['total'],
                gpu_info['name'],
                {"ui": {"text": status_display}}
            )
            
        except Exception as e:
            current_time = time.strftime("%H:%M:%S", time.localtime())
            error_msg = f"💥 [{current_time}] GPU monitoring error: {str(e)}"
            print(error_msg)
            return (
                error_msg,
                0.0,
                0.0,
                0.0,
                "Error",
                {"ui": {"text": error_msg}}
            )


# ComfyUI node registration
NODE_CLASS_MAPPINGS = {
    "StrawberryVramOptimizer": StrawberryVramOptimizer,
    "StrawberryGPUMonitor": StrawberryGPUMonitor
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "StrawberryVramOptimizer": "StFist - VRAM Optimizer",
    "StrawberryGPUMonitor": "StFist - GPU Monitor"
}