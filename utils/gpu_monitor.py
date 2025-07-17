import time
from .dependency_installer import get_gputil_or_mock

class GPUMonitor:
    """GPU 메모리 모니터링 클래스"""
    
    def __init__(self):
        self.GPUtil = get_gputil_or_mock()
    
    def get_gpu_info(self):
        """GPU 정보 가져오기"""
        try:
            gpus = self.GPUtil.getGPUs()
            if not gpus:
                return None
            
            gpu = gpus[0]
            return {
                'name': gpu.name,
                'total': gpu.memoryTotal,
                'used': gpu.memoryUsed,
                'percent': gpu.memoryUtil * 100
            }
        except Exception as e:
            print(f"🍓 [StrawberryFist] GPU 정보 가져오기 실패: {e}")
            return None
    
    def generate_memory_bar(self, percent, bar_length=25):
        """메모리 사용률 시각화 바 생성"""
        filled_length = int(round(bar_length * percent / 100))
        
        # 사용률에 따른 색상 및 이모지 설정
        if percent < 30:
            color_bar = '🟢' * filled_length + '⬜' * (bar_length - filled_length)
            status_emoji = '✅'
            status_color = 'GOOD'
        elif percent < 70:
            color_bar = '🟡' * filled_length + '⬜' * (bar_length - filled_length)
            status_emoji = '⚠️'
            status_color = 'WARNING'
        else:
            color_bar = '🔴' * filled_length + '⬜' * (bar_length - filled_length)
            status_emoji = '🚨'
            status_color = 'CRITICAL'
        
        return {
            'bar': color_bar,
            'emoji': status_emoji,
            'color': status_color
        }
    
    def log_gpu_status(self, execution_count=0):
        """GPU 상태 로그 출력"""
        current_time = time.strftime("%H:%M:%S", time.localtime())
        gpu_info = self.get_gpu_info()
        
        if gpu_info:
            print(f"📊 [{current_time}] GPU 메모리 상태: {gpu_info['used']:.1f}MB / {gpu_info['total']:.1f}MB ({gpu_info['percent']:.1f}%)")
            return True
        else:
            print(f"❌ [{current_time}] GPU 정보를 가져올 수 없습니다.")
            return False
    
    def should_clean_memory(self, auto_clean_mode, threshold=70):
        """메모리 정리 필요 여부 판단"""
        if auto_clean_mode == "Every Time":
            return True
        
        gpu_info = self.get_gpu_info()
        if not gpu_info:
            return False
        
        if auto_clean_mode == "Only When High" and gpu_info['percent'] >= threshold:
            return True
        
        return False