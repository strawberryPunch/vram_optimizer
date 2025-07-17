import time

class ComfyUIHooks:
    """ComfyUI 훅 시스템 관리 클래스"""
    
    def __init__(self, optimizer_instance):
        self.optimizer_instance = optimizer_instance
    
    def register_execution_hooks(self):
        """execution 모듈 훅 등록"""
        try:
            import execution
            
            if hasattr(execution, '_strawberry_hooked'):
                return
            
            original_execute = execution.PromptExecutor.execute
            
            def hooked_execute(self_executor, prompt, prompt_id, extra_data={}, execute_outputs=[]):
                current_time = time.strftime("%H:%M:%S", time.localtime())
                
                # 큐 실행 전 정리
                if self.optimizer_instance.settings['run_timing'] in ['Before Queue', 'Both']:
                    print(f"\n🔥 [{current_time}] ═══ 큐 실행 전 VRAM 정리 시작 (ID: {prompt_id}) ═══")
                    self.optimizer_instance.perform_vram_cleanup(reason=f"큐 실행 전 (ID: {prompt_id})")
                    print(f"🔥 [{current_time}] ═══ 큐 실행 전 VRAM 정리 완료 ═══\n")
                
                # 원래 실행
                result = original_execute(self_executor, prompt, prompt_id, extra_data, execute_outputs)
                
                # 큐 실행 후 정리
                if self.optimizer_instance.settings['run_timing'] in ['After Queue', 'Both']:
                    print(f"\n🔥 [{current_time}] ═══ 큐 실행 후 VRAM 정리 시작 (ID: {prompt_id}) ═══")
                    self.optimizer_instance.perform_vram_cleanup(reason=f"큐 실행 후 (ID: {prompt_id})")
                    print(f"🔥 [{current_time}] ═══ 큐 실행 후 VRAM 정리 완료 ═══\n")
                
                return result
            
            execution.PromptExecutor.execute = hooked_execute
            execution._strawberry_hooked = True
            print(f"🍓 [StrawberryFist] execution 훅 등록 완료!")
            
        except Exception as e:
            print(f"🍓 [StrawberryFist] execution 훅 등록 실패: {e}")
            raise
    
    def register_server_hooks(self):
        """server 모듈 훅 등록"""
        try:
            import server
            
            if hasattr(server, '_strawberry_server_hooked'):
                return
            
            # PromptServer 후킹 시도
            if hasattr(server, 'PromptServer'):
                original_prompt_handler = None
                
                # 기존 핸들러 찾기
                for handler in server.PromptServer.instance.app.router._resources:
                    if hasattr(handler, '_path') and '/prompt' in str(handler._path):
                        original_prompt_handler = handler
                        break
                
                print(f"🍓 [StrawberryFist] server 훅 등록 시도...")
                server._strawberry_server_hooked = True
                
        except Exception as e:
            print(f"🍓 [StrawberryFist] server 훅 등록 실패: {e}")
            raise
    
    def try_register_hooks(self):
        """다양한 방법으로 훅 등록 시도"""
        try:
            # 방법 1: execution 모듈 훅
            self.register_execution_hooks()
        except Exception as e:
            print(f"🍓 [StrawberryFist] execution 훅 실패: {e}")
            
        try:
            # 방법 2: server 모듈 훅
            self.register_server_hooks()
        except Exception as e:
            print(f"🍓 [StrawberryFist] server 훅 실패: {e}")