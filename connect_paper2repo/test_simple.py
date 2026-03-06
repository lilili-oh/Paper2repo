#!/usr/bin/env python3
"""
简化功能测试脚本 - 不依赖spaCy
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
        from src.processors.code_processor import CodeProcessor
        print("✅ Code processor imported successfully")
    except Exception as e:
        print(f"❌ Code processor import failed: {e}")
        return False
    
    try:
        from src.services.github_service import GitHubService
        print("✅ GitHub service imported successfully")
    except Exception as e:
        print(f"❌ GitHub service import failed: {e}")
        return False
    
    return True

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

def test_models():
    """测试数据模型"""
    print("\n🧪 Testing data models...")
    
    try:
        from src.models.text_model import TextDocument, TextFeature
        from src.models.code_model import CodeFile, CodeLanguage
        from src.models.alignment_model import AlignmentResult
        
        # 测试文本模型
        text_doc = TextDocument(
            id="test_1",
            title="Test Document",
            content="This is a test document.",
            source="test"
        )
        print(f"✅ Text document created: {text_doc.title}")
        
        # 测试代码模型
        code_file = CodeFile(
            id="test_2",
            filename="test.py",
            filepath="test.py",
            language=CodeLanguage.PYTHON,
            content="def hello(): pass",
            size=20
        )
        print(f"✅ Code file created: {code_file.filename}")
        
        # 测试对齐结果模型
        alignment = AlignmentResult(
            id="test_3",
            text_document_id="test_1",
            code_repository_id="test_2"
        )
        print(f"✅ Alignment result created: {alignment.id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Model test failed: {e}")
        return False

def test_code_processing():
    """测试代码处理（不依赖spaCy）"""
    print("\n🧪 Testing code processing...")
    
    try:
        from src.processors.code_processor import CodeProcessor
        
        # 创建代码处理器
        code_processor = CodeProcessor()
        
        # 测试简单Python代码
        test_code = '''
def hello_world():
    """Print hello world message"""
    print("Hello, World!")
    return "success"

class TestClass:
    def __init__(self):
        self.value = 42
    
    def get_value(self):
        return self.value
'''
        
        # 处理代码文件
        code_file = code_processor.process_file("test.py", test_code)
        
        print(f"✅ Code file processed: {code_file.filename}")
        print(f"✅ Language detected: {code_file.language}")
        print(f"✅ Features extracted: {len(code_file.features)}")
        print(f"✅ Functions found: {len(code_file.functions)}")
        print(f"✅ Classes found: {len(code_file.classes)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Code processing test failed: {e}")
        return False

def main():
    """主测试函数"""
    print("🔗 Paper-Code Alignment Tool - Simple Tests")
    print("=" * 50)
    
    # 运行测试
    tests = [
        ("Import Test", test_imports),
        ("Configuration Test", test_config),
        ("Data Models Test", test_models),
        ("Code Processing Test", test_code_processing)
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
        print("🎉 All tests passed! The core functionality is working.")
        print("\n📝 Note: For full functionality, you need to install:")
        print("   pip install spacy")
        print("   python -m spacy download en_core_web_sm")
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
