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
        """Log cleanup progress"""
        print(f"⚡ [{current_time}] VRAM cleanup in progress... ({self.clear_mode} mode)")
        print(f"   🔧 Executing torch.cuda.empty_cache()...")
        
        if self.clear_mode == "Aggressive":
            print(f"   🔧 Executing gc.collect()...")
            if hasattr(torch.cuda, 'synchronize'):
                print(f"   🔧 Executing torch.cuda.synchronize()...")
    
    def log_cleanup_result(self, result, current_time):
        """Log cleanup result"""
        if result['success']:
            if result['cleared'] > 0:
                print(f"🎉 [{current_time}] VRAM cleanup successful! {result['before']:.1f}MB → {result['after']:.1f}MB (freed: {result['cleared']:.1f}MB)")
            else:
                print(f"✨ [{current_time}] Already optimized (current: {result['after']:.1f}MB)")
        else:
            print(f"❌ [{current_time}] VRAM cleanup failed: {result['error']}")
    
    def generate_ui_message(self, result, current_time, execution_count):
        """Generate UI message"""
        execution_info = f"[Execution#{execution_count}] "
        
        if result['success']:
            if result['cleared'] > 0:
                return f"🎉 {execution_info}[{current_time}] VRAM cleanup completed! Freed: {result['cleared']:.1f}MB"
            else:
                return f"✨ {execution_info}[{current_time}] Already optimized ({result['after']:.1f}MB)"
        else:
            return f"❌ {execution_info}[{current_time}] {result['error']}"