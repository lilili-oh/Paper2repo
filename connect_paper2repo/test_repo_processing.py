#!/usr/bin/env python3
"""
测试仓库处理功能
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.github_service import GitHubService
from config import settings

def test_repository_processing():
    """测试仓库处理功能"""
    print("Testing Repository Processing")
    print("=" * 50)
    
    # 初始化GitHub服务
    print("Initializing GitHub service...")
    github_service = GitHubService()
    
    # 测试一个简单的仓库
    test_repos = [
        ("octocat", "Hello-World"),  # GitHub官方示例仓库
        ("microsoft", "vscode"),     # 大型仓库
        ("torvalds", "linux"),       # 超大型仓库
    ]
    
    for owner, repo_name in test_repos:
        print(f"\nTesting repository: {owner}/{repo_name}")
        print("-" * 30)
        
        try:
            # 测试获取仓库信息
            print("1. Testing get_repository_info...")
            repo_info = github_service.get_repository_info(owner, repo_name)
            print(f"   ✓ Repository info: {repo_info['name']}")
            print(f"   ✓ Stars: {repo_info.get('stars', 'N/A')}")
            print(f"   ✓ Language: {repo_info.get('language', 'N/A')}")
            
            # 测试获取文件列表
            print("2. Testing get_repository_files...")
            files_data = github_service.get_repository_files(owner, repo_name, max_files=5)
            print(f"   ✓ Found {len(files_data)} files")
            
            if files_data:
                for file_data in files_data[:3]:  # 显示前3个文件
                    print(f"   - {file_data['path']} ({len(file_data['content'])} chars)")
            
            # 测试创建代码仓库对象
            print("3. Testing create_code_repository...")
            code_repo = github_service.create_code_repository(owner, repo_name, max_files=5)
            print(f"   ✓ Created repository object")
            print(f"   ✓ Total files: {code_repo.total_files}")
            print(f"   ✓ Total lines: {code_repo.total_lines}")
            print(f"   ✓ Languages: {list(code_repo.languages)}")
            
            # 显示处理结果
            if code_repo.files:
                print(f"   ✓ Processed files:")
                for file in code_repo.files[:3]:  # 显示前3个文件
                    print(f"     - {file.filename} ({len(file.features)} features)")
            
            print(f"   ✓ Repository processing successful!")
            
        except Exception as e:
            print(f"   ✗ Error: {e}")
            import traceback
            traceback.print_exc()
        
        # 只测试第一个仓库
        break

if __name__ == "__main__":
    test_repository_processing()
