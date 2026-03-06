#!/usr/bin/env python3
"""
简单测试仓库处理功能
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_code_processor():
    """测试代码处理器"""
    print("Testing Code Processor")
    print("=" * 50)
    
    try:
        from src.processors.code_processor import CodeProcessor
        
        # 初始化代码处理器
        print("1. Initializing CodeProcessor...")
        processor = CodeProcessor()
        print("   ✓ CodeProcessor initialized successfully")
        
        # 测试处理Python文件
        print("2. Testing Python file processing...")
        python_code = '''
def hello_world():
    """A simple hello world function"""
    print("Hello, World!")
    return "success"

class TestClass:
    def __init__(self):
        self.name = "test"
    
    def method_one(self):
        return self.name
'''
        
        code_file = processor.process_file("test.py", python_code)
        print(f"   ✓ Processed Python file: {code_file.filename}")
        print(f"   ✓ Language: {code_file.language}")
        print(f"   ✓ Features found: {len(code_file.features)}")
        print(f"   ✓ Functions: {len(code_file.functions)}")
        print(f"   ✓ Classes: {len(code_file.classes)}")
        
        # 显示特征详情
        for feature in code_file.features[:3]:
            print(f"     - {feature.feature_type}: {feature.name}")
        
        print("   ✓ Python processing successful!")
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()

def test_storage_service():
    """测试存储服务"""
    print("\nTesting Storage Service")
    print("=" * 50)
    
    try:
        from src.services.storage_service import StorageService
        
        # 初始化存储服务
        print("1. Initializing StorageService...")
        storage = StorageService()
        print("   ✓ StorageService initialized successfully")
        
        # 测试存储统计
        print("2. Testing storage stats...")
        stats = storage.get_storage_stats()
        print(f"   ✓ Storage stats retrieved: {stats}")
        
        print("   ✓ Storage service test successful!")
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_code_processor()
    test_storage_service()
