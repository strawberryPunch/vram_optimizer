import sys
import subprocess
import os

def install_dependencies():
    """필요한 패키지 자동 설치"""
    required_packages = [
        'GPUtil',
    ]
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"🍓 [StrawberryFist] {package} 이미 설치됨")
        except ImportError:
            print(f"🍓 [StrawberryFist] {package} 설치 중...")
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", package,
                    "--no-warn-script-location"
                ])
                print(f"🍓 [StrawberryFist] {package} 설치 완료!")
            except subprocess.CalledProcessError as e:
                print(f"🍓 [StrawberryFist] {package} 설치 실패: {e}")
                # 대안 설치 시도
                try:
                    subprocess.check_call([
                        sys.executable, "-m", "pip", "install", package,
                        "--user", "--no-warn-script-location"
                    ])
                    print(f"🍓 [StrawberryFist] {package} 사용자 모드로 설치 완료!")
                except subprocess.CalledProcessError:
                    print(f"🍓 [StrawberryFist] {package} 설치 실패 - 수동 설치 필요")

def install_from_requirements():
    """requirements.txt에서 종속성 설치"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    requirements_file = os.path.join(parent_dir, "requirements.txt")
    
    if os.path.exists(requirements_file):
        print(f"🍓 [StrawberryFist] requirements.txt에서 종속성 설치 중...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", requirements_file,
                "--no-warn-script-location"
            ])
            print(f"🍓 [StrawberryFist] requirements.txt 설치 완료!")
        except subprocess.CalledProcessError as e:
            print(f"🍓 [StrawberryFist] requirements.txt 설치 실패: {e}")
            # 개별 설치로 대체
            install_dependencies()
    else:
        print(f"🍓 [StrawberryFist] requirements.txt 파일이 없습니다. 개별 설치 진행...")
        install_dependencies()

def get_gputil_or_mock():
    """GPUtil 가져오기 또는 Mock 클래스 반환"""
    try:
        import GPUtil
        return GPUtil
    except ImportError:
        print("🍓 [StrawberryFist] GPUtil을 가져올 수 없습니다. Mock 클래스를 사용합니다.")
        
        class GPUtilMock:
            @staticmethod
            def getGPUs():
                return []
        
        return GPUtilMock