#!/usr/bin/env python3
"""
基本功能测试脚本
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """测试模块导入"""
    print("🧪 Testing imports...")
    
    try:
        from src.models.text_model import TextDocument, TextFeature
        from src.models.code_model import CodeFile, CodeRepository, CodeLanguage
        from src.models.alignment_model import AlignmentResult, AlignmentMatch
        print("✅ Models imported successfully")
    except Exception as e:
        print(f"❌ Model import failed: {e}")
        return False
    
    try:
        from src.processors.text_processor import TextProcessor
        from src.processors.code_processor import CodeProcessor
        from src.processors.alignment_processor import AlignmentProcessor
        print("✅ Processors imported successfully")
    except Exception as e:
        print(f"❌ Processor import failed: {e}")
        return False
    
    try:
        from src.services.github_service import GitHubService
        from src.services.storage_service import StorageService
        print("✅ Services imported successfully")
    except Exception as e:
        print(f"❌ Service import failed: {e}")
        return False
    
    try:
        from src.visualization.alignment_visualizer import AlignmentVisualizer
        from src.visualization.similarity_visualizer import SimilarityVisualizer
        print("✅ Visualizers imported successfully")
    except Exception as e:
        print(f"❌ Visualizer import failed: {e}")
        return False
    
    return True

def test_basic_functionality():
    """测试基本功能"""
    print("\n🧪 Testing basic functionality...")
    
    try:
        # 测试文本处理器
        from src.processors.text_processor import TextProcessor
        text_processor = TextProcessor()
        
        # 测试简单文本处理
        test_text = "This is a test sentence. It contains multiple sentences for testing purposes."
        sentences = text_processor.extract_sentences(test_text)
        print(f"✅ Text processing: {len(sentences)} sentences extracted")
        
        # 测试代码处理器
        from src.processors.code_processor import CodeProcessor
        code_processor = CodeProcessor()
        
        # 测试简单代码处理
        test_code = """
def hello_world():
    print("Hello, World!")
    return "success"

class TestClass:
    def __init__(self):
        self.value = 42
"""
        code_file = code_processor.process_file("test.py", test_code)
        print(f"✅ Code processing: {len(code_file.features)} features extracted")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

def test_config():
    """测试配置"""
    print("\n🧪 Testing configuration...")
    
    try:
        from config import settings
        print(f"✅ Configuration loaded: {settings.embedding_model}")
        print(f"✅ Similarity threshold: {settings.similarity_threshold}")
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def main():
    """主测试函数"""
    print("🔗 Paper-Code Alignment Tool - Basic Tests")
    print("=" * 50)
    
    # 运行测试
    tests = [
        ("Import Test", test_imports),
        ("Configuration Test", test_config),
        ("Basic Functionality Test", test_basic_functionality)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        if test_func():
            passed += 1
            print(f"✅ {test_name} passed")
        else:
            print(f"❌ {test_name} failed")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The application is ready to run.")
        print("\n🚀 To start the application, run:")
        print("   python run.py")
        print("   or")
        print("   streamlit run main.py")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
