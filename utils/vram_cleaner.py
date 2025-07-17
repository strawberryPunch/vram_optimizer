import torch
import gc
import time

class VRAMCleaner:
    """VRAM 정리 전용 클래스"""
    
    def __init__(self, clear_mode="Standard"):
        self.clear_mode = clear_mode
    
    def is_cuda_available(self):
        """CUDA 사용 가능 여부 확인"""
        return torch.cuda.is_available()
    
    def get_allocated_memory(self):
        """현재 할당된 VRAM 메모리 크기 (MB)"""
        if self.is_cuda_available():
            return torch.cuda.memory_allocated() / 1024**2
        return 0
    
    def perform_cleanup(self):
        """VRAM 정리 실행"""
        if not self.is_cuda_available():
            return {
                'success': False,
                'error': 'CUDA 사용 불가',
                'before': 0,
                'after': 0,
                'cleared': 0
            }
        
        try:
            before = self.get_allocated_memory()
            
            # 기본 정리
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()
            
            # Aggressive 모드일 때 추가 정리
            if self.clear_mode == "Aggressive":
                gc.collect()
                if hasattr(torch.cuda, 'synchronize'):
                    torch.cuda.synchronize()
            
            after = self.get_allocated_memory()
            cleared = before - after
            
            return {
                'success': True,
                'before': before,
                'after': after,
                'cleared': cleared,
                'mode': self.clear_mode
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'before': 0,
                'after': 0,
                'cleared': 0
            }
    
    def log_cleanup_progress(self, current_time):
        """정리 진행 상황 로그"""
        print(f"⚡ [{current_time}] VRAM 정리 진행... ({self.clear_mode} 모드)")
        print(f"   🔧 torch.cuda.empty_cache() 실행중...")
        
        if self.clear_mode == "Aggressive":
            print(f"   🔧 gc.collect() 실행중...")
            if hasattr(torch.cuda, 'synchronize'):
                print(f"   🔧 torch.cuda.synchronize() 실행중...")
    
    def log_cleanup_result(self, result, current_time):
        """정리 결과 로그"""
        if result['success']:
            if result['cleared'] > 0:
                print(f"🎉 [{current_time}] VRAM 정리 성공! {result['before']:.1f}MB → {result['after']:.1f}MB (해제: {result['cleared']:.1f}MB)")
            else:
                print(f"✨ [{current_time}] 이미 최적화된 상태 (현재: {result['after']:.1f}MB)")
        else:
            print(f"❌ [{current_time}] VRAM 정리 실패: {result['error']}")
    
    def generate_ui_message(self, result, current_time, execution_count):
        """UI 메시지 생성"""
        execution_info = f"[실행#{execution_count}] "
        
        if result['success']:
            if result['cleared'] > 0:
                return f"🎉 {execution_info}[{current_time}] VRAM 정리 완료! 해제: {result['cleared']:.1f}MB"
            else:
                return f"✨ {execution_info}[{current_time}] 이미 최적화된 상태 ({result['after']:.1f}MB)"
        else:
            return f"❌ {execution_info}[{current_time}] {result['error']}"