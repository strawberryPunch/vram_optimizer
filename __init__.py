import time
import threading

# 종속성 자동 설치 실행
try:
    from .utils import install_from_requirements
    install_from_requirements()
    print("🍓 [StrawberryFist] 모든 종속성 로드 완료!")
except Exception as e:
    print(f"🍓 [StrawberryFist] 종속성 설치 중 오류 발생: {e}")

# 필요한 모듈 import
from .utils import GPUMonitor, VRAMCleaner
from .hooks import ComfyUIHooks

class StrawberryVramOptimizer:
    """StrawberryFist VRAM 최적화 노드"""
    
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
            
            # 컴포넌트 초기화
            self.gpu_monitor = GPUMonitor()
            self.vram_cleaner = VRAMCleaner()
            self.hooks = ComfyUIHooks(self)
            
            # 즉시 서버 실행 시 훅 시도
            self.hooks.try_register_hooks()
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "enabled": (
                    ["On", "Off"],
                    {
                        "default": "On",
                        "tooltip": "제작자 : StrawberryFist\n\n각 큐 실행 후 VRAM을 자동으로 비웁니다."
                    }
                ),
                "clear_mode": (
                    ["Standard", "Aggressive"],
                    {
                        "default": "Standard",
                        "tooltip": "Standard: 기본 VRAM 정리\nAggressive: 추가적인 메모리 정리 포함"
                    }
                ),
                "auto_clean": (
                    ["Every Time", "Only When High"],
                    {
                        "default": "Every Time",
                        "tooltip": "Every Time: 매번 실행\nOnly When High: VRAM 사용률이 70% 이상일 때만 실행"
                    }
                ),
                "run_timing": (
                    ["After Queue", "Before Queue", "Both"],
                    {
                        "default": "After Queue",
                        "tooltip": "After Queue: 큐 실행 후 정리\nBefore Queue: 큐 실행 전 정리\nBoth: 실행 전후 모두"
                    }
                ),
                "force_run": (
                    "INT",
                    {
                        "default": 0,
                        "min": 0,
                        "max": 999,
                        "step": 1,
                        "tooltip": "이 값을 변경하면 수동으로 VRAM 정리 실행"
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
        # 항상 다른 값으로 인식하여 캐시 방지
        return time.time()
    
    def setup_and_run(self, enabled, clear_mode, auto_clean, run_timing, force_run):
        current_time = time.strftime("%H:%M:%S", time.localtime())
        
        # 설정 변경 감지
        old_settings = self.settings.copy()
        new_settings = {
            'enabled': enabled == "On",
            'clear_mode': clear_mode,
            'auto_clean': auto_clean,
            'run_timing': run_timing
        }
        
        # 설정이 변경되었는지 확인
        settings_changed = (old_settings != new_settings)
        force_run_changed = (force_run != self.last_force_run)
        
        # 변경 사항 로그
        if settings_changed:
            print(f"\n⚙️ [{current_time}] ═══ 설정 변경 감지 ═══")
            for key, value in new_settings.items():
                if old_settings.get(key) != value:
                    print(f"   📝 {key}: {old_settings.get(key)} → {value}")
            print(f"⚙️ [{current_time}] ═══ 설정 변경 완료 ═══\n")
        
        # 설정 업데이트
        self.settings.update(new_settings)
        self.last_force_run = force_run
        
        # VRAM 정리 모드 업데이트
        self.vram_cleaner.clear_mode = clear_mode
        
        # 훅 등록 시도 (설정 변경 시마다)
        if settings_changed:
            self.hooks.try_register_hooks()
        
        # 실행 조건 확인
        should_run = False
        run_reason = ""
        
        if force_run_changed and force_run > 0:
            should_run = True
            run_reason = f"수동 실행 (트리거: {force_run})"
        elif settings_changed:
            should_run = True
            run_reason = "설정 변경 후 자동 실행"
        elif self.execution_count == 0:
            should_run = True
            run_reason = "초기 실행"
        
        # 실행 또는 상태 확인
        if should_run:
            if force_run_changed and force_run > 0:
                print(f"\n🔧 [{current_time}] ═══ 수동 VRAM 정리 실행 (트리거: {force_run}) ═══")
            elif settings_changed:
                print(f"\n🔧 [{current_time}] ═══ 설정 변경 후 VRAM 정리 실행 ═══")
            
            result = self.perform_vram_cleanup(force_run=True, reason=run_reason)
            
            if force_run_changed and force_run > 0:
                print(f"🔧 [{current_time}] ═══ 수동 VRAM 정리 완료 ═══\n")
            elif settings_changed:
                print(f"🔧 [{current_time}] ═══ 설정 변경 후 VRAM 정리 완료 ═══\n")
        else:
            # 설정 변경 없이 단순 상태 확인
            result = self.get_current_status()
        
        return result
    
    def perform_vram_cleanup(self, force_run=False, reason="자동 실행"):
        """VRAM 정리 실행"""
        try:
            current_time = time.strftime("%H:%M:%S", time.localtime())
            self.execution_count += 1
            
            # 실행 로그
            print(f"🎯 [{current_time}] VRAM 정리 시작 - {reason} (실행 횟수: {self.execution_count})")
            
            # 비활성화 상태 체크
            if not self.settings['enabled'] and not force_run:
                disabled_msg = f"⏸️ [실행#{self.execution_count}] [{current_time}] VRAM 정리 비활성화 상태"
                print(disabled_msg)
                return {
                    "ui": {"text": disabled_msg},
                    "result": (disabled_msg,)
                }
            
            # GPU 정보 확인
            gpu_info = self.gpu_monitor.get_gpu_info()
            if not gpu_info:
                error_msg = f"❌ [실행#{self.execution_count}] [{current_time}] GPU를 찾을 수 없습니다."
                print(error_msg)
                return {
                    "ui": {"text": error_msg},
                    "result": (error_msg,)
                }
            
            # GPU 상태 로그
            self.gpu_monitor.log_gpu_status(self.execution_count)
            
            # 정리 실행 조건 확인
            should_clean = self.settings['enabled'] or force_run
            if should_clean and not self.gpu_monitor.should_clean_memory(self.settings['auto_clean']):
                should_clean = False
                skip_msg = f"ℹ️ [실행#{self.execution_count}] [{current_time}] VRAM 사용률 {gpu_info['percent']:.1f}% < 70% → 정리 건너뜀"
                print(skip_msg)
                return {
                    "ui": {"text": skip_msg},
                    "result": (skip_msg,)
                }
            
            # VRAM 정리 실행
            if should_clean:
                # 진행 상황 로그
                self.vram_cleaner.log_cleanup_progress(current_time)
                
                # 정리 실행
                cleanup_result = self.vram_cleaner.perform_cleanup()
                
                # 결과 로그
                self.vram_cleaner.log_cleanup_result(cleanup_result, current_time)
                
                # UI 메시지 생성
                ui_message = self.vram_cleaner.generate_ui_message(cleanup_result, current_time, self.execution_count)
                
                # 최종 상태 로그
                final_status = "CLEANED" if cleanup_result['success'] and cleanup_result['cleared'] > 0 else "ALREADY_CLEAN"
                print(f"🍓 [{current_time}] 최종 상태: {final_status}")
                
                return {
                    "ui": {"text": ui_message},
                    "result": (ui_message,)
                }
            
            # 비활성화 상태
            disabled_msg = f"⏸️ [실행#{self.execution_count}] [{current_time}] VRAM 정리 비활성화 상태"
            return {
                "ui": {"text": disabled_msg},
                "result": (disabled_msg,)
            }
            
        except Exception as e:
            current_time = time.strftime("%H:%M:%S", time.localtime())
            error_msg = f"💥 [실행#{self.execution_count}] [{current_time}] VRAM 정리 오류: {str(e)}"
            print(f"💥 [{current_time}] VRAM 정리 오류: {str(e)}")
            return {
                "ui": {"text": error_msg},
                "result": (error_msg,)
            }
    
    def get_current_status(self):
        """현재 상태만 확인 (정리 실행 없이)"""
        try:
            current_time = time.strftime("%H:%M:%S", time.localtime())
            
            # GPU 정보 확인
            gpu_info = self.gpu_monitor.get_gpu_info()
            if not gpu_info:
                error_msg = f"❌ [확인#{self.execution_count}] [{current_time}] GPU를 찾을 수 없습니다."
                return {
                    "ui": {"text": error_msg},
                    "result": (error_msg,)
                }
            
            # 현재 상태 로그
            print(f"📊 [{current_time}] 현재 상태 확인 - GPU 사용률: {gpu_info['percent']:.1f}%")
            
            status_msg = f"📊 [확인#{self.execution_count}] [{current_time}] 현재 상태 - GPU 사용률: {gpu_info['percent']:.1f}%"
            return {
                "ui": {"text": status_msg},
                "result": (status_msg,)
            }
            
        except Exception as e:
            current_time = time.strftime("%H:%M:%S", time.localtime())
            error_msg = f"💥 [확인#{self.execution_count}] [{current_time}] 상태 확인 오류: {str(e)}"
            return {
                "ui": {"text": error_msg},
                "result": (error_msg,)
            }


class StrawberryGPUMonitor:
    """실시간 GPU 모니터링 노드"""
    
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
                        "tooltip": "실시간 GPU 모니터링 활성화/비활성화"
                    }
                ),
                "update_interval": (
                    "FLOAT",
                    {
                        "default": 1.0,
                        "min": 0.1,
                        "max": 10.0,
                        "step": 0.1,
                        "tooltip": "모니터링 업데이트 간격 (초)"
                    }
                ),
                "history_length": (
                    "INT",
                    {
                        "default": 60,
                        "min": 10,
                        "max": 300,
                        "step": 1,
                        "tooltip": "히스토리 유지 개수 (개)"
                    }
                ),
                "warning_threshold": (
                    "FLOAT",
                    {
                        "default": 80.0,
                        "min": 50.0,
                        "max": 95.0,
                        "step": 5.0,
                        "tooltip": "경고 임계값 (%)"
                    }
                ),
                "refresh_trigger": (
                    "INT",
                    {
                        "default": 0,
                        "min": 0,
                        "max": 9999,
                        "step": 1,
                        "tooltip": "값 변경 시 즉시 업데이트"
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
        """백그라운드 모니터링 시작"""
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
                        
                        # 히스토리 추가
                        self.monitor_data['history'].append({
                            'time': current_time,
                            'percent': gpu_info['percent'],
                            'used': gpu_info['used']
                        })
                        
                        # 히스토리 길이 제한
                        if len(self.monitor_data['history']) > history_length:
                            self.monitor_data['history'].pop(0)
                        
                        # 경고 체크
                        if gpu_info['percent'] > warning_threshold:
                            print(f"🚨 [GPU 경고] 메모리 사용률: {gpu_info['percent']:.1f}% (임계값: {warning_threshold}%)")
                    
                    time.sleep(update_interval)
                except Exception as e:
                    print(f"🍓 [GPU 모니터링] 오류: {e}")
                    time.sleep(update_interval)
        
        self._monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self._monitor_thread.start()
        print(f"🍓 [GPU 모니터링] 시작 - 간격: {update_interval}초")
    
    def stop_monitoring(self):
        """백그라운드 모니터링 중지"""
        if self._is_monitoring:
            self._is_monitoring = False
            if self._monitor_thread:
                self._monitor_thread.join(timeout=1)
            print("🍓 [GPU 모니터링] 중지")
    
    def generate_status_display(self, warning_threshold):
        """상태 표시 생성"""
        data = self.monitor_data
        current_time = time.strftime("%H:%M:%S", time.localtime())
        
        # 메모리 바 생성
        bar_info = self.gpu_monitor.generate_memory_bar(data['current_percent'])
        
        # 상태 메시지 생성
        status_lines = []
        status_lines.append(f"🎮 ═══════════════════════════════════════════════════════════")
        status_lines.append(f"🔥 StrawberryFist GPU 실시간 모니터링 [{current_time}]")
        status_lines.append(f"═══════════════════════════════════════════════════════════")
        status_lines.append(f"")
        
        # GPU 정보
        status_lines.append(f"📊 GPU: {data['gpu_name']}")
        status_lines.append(f"┌─────────────────────────────────────────────────────────┐")
        status_lines.append(f"│ {bar_info['emoji']} 사용률: {data['current_percent']:.1f}% ({bar_info['color']})                    │")
        status_lines.append(f"│ 📈 사용량: {data['current_used']:.1f}MB / {data['current_total']:.1f}MB                   │")
        status_lines.append(f"│ {bar_info['bar']} │")
        status_lines.append(f"└─────────────────────────────────────────────────────────┘")
        status_lines.append(f"")
        
        # 히스토리 정보
        if len(data['history']) > 1:
            recent_history = data['history'][-10:]  # 최근 10개
            avg_percent = sum(h['percent'] for h in recent_history) / len(recent_history)
            max_percent = max(h['percent'] for h in recent_history)
            min_percent = min(h['percent'] for h in recent_history)
            
            status_lines.append(f"📈 최근 통계 (최근 {len(recent_history)}개 샘플)")
            status_lines.append(f"┌─────────────────────────────────────────────────────────┐")
            status_lines.append(f"│ 평균: {avg_percent:.1f}% | 최대: {max_percent:.1f}% | 최소: {min_percent:.1f}% │")
            status_lines.append(f"│ 경고 임계값: {warning_threshold:.1f}%                          │")
            status_lines.append(f"└─────────────────────────────────────────────────────────┘")
            status_lines.append(f"")
        
        # 트렌드 분석
        if len(data['history']) >= 5:
            recent_5 = [h['percent'] for h in data['history'][-5:]]
            if recent_5[-1] > recent_5[0]:
                trend = "📈 증가 추세"
            elif recent_5[-1] < recent_5[0]:
                trend = "📉 감소 추세"
            else:
                trend = "➡️ 안정적"
            
            status_lines.append(f"📊 트렌드: {trend}")
            status_lines.append(f"")
        
        # 경고 메시지
        if data['current_percent'] > warning_threshold:
            status_lines.append(f"🚨 경고: 메모리 사용률이 임계값을 초과했습니다!")
            status_lines.append(f"")
        
        status_lines.append(f"🍓 실시간 모니터링 활성화 중... 🍓")
        
        return "\n".join(status_lines)
    
    def monitor_gpu(self, monitoring_enabled, update_interval, history_length, warning_threshold, refresh_trigger):
        """GPU 모니터링 메인 함수"""
        try:
            current_time = time.strftime("%H:%M:%S", time.localtime())
            
            # 모니터링 상태 제어
            if monitoring_enabled == "On":
                if not self._is_monitoring:
                    self.start_monitoring(update_interval, history_length, warning_threshold)
            else:
                if self._is_monitoring:
                    self.stop_monitoring()
                
                # 모니터링 비활성화 메시지
                disabled_msg = f"⏸️ [{current_time}] GPU 실시간 모니터링 비활성화 상태"
                return (
                    disabled_msg,
                    0.0,
                    0.0,
                    0.0,
                    "Unknown",
                    {"ui": {"text": disabled_msg}}
                )
            
            # 현재 GPU 정보 가져오기
            gpu_info = self.gpu_monitor.get_gpu_info()
            if not gpu_info:
                error_msg = f"❌ [{current_time}] GPU 정보를 가져올 수 없습니다."
                return (
                    error_msg,
                    0.0,
                    0.0,
                    0.0,
                    "Error",
                    {"ui": {"text": error_msg}}
                )
            
            # 실시간 로그 (선택적)
            if refresh_trigger > 0:
                print(f"🔄 [{current_time}] GPU 상태 업데이트 - 사용률: {gpu_info['percent']:.1f}%")
            
            # 상태 표시 생성
            status_display = self.generate_status_display(warning_threshold)
            
            # 간단한 상태 문자열
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
            error_msg = f"💥 [{current_time}] GPU 모니터링 오류: {str(e)}"
            print(error_msg)
            return (
                error_msg,
                0.0,
                0.0,
                0.0,
                "Error",
                {"ui": {"text": error_msg}}
            )


# ComfyUI 노드 등록
NODE_CLASS_MAPPINGS = {
    "StrawberryVramOptimizer": StrawberryVramOptimizer,
    "StrawberryGPUMonitor": StrawberryGPUMonitor
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "StrawberryVramOptimizer": "StFist - VRAM Optimizer",
    "StrawberryGPUMonitor": "StFist - GPU Monitor"
}