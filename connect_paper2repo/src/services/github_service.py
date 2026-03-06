"""
GitHub服务 - 负责从GitHub获取代码仓库
"""
import os
import base64
from typing import List, Dict, Any, Optional, Tuple
from github import Github, GithubException
from github.Repository import Repository
from github.ContentFile import ContentFile
import requests
from urllib.parse import urlparse

from ..models.code_model import CodeRepository, CodeFile, CodeLanguage
from ..processors.code_processor import CodeProcessor
from config import settings

class GitHubService:
    """GitHub服务类"""
    
    def __init__(self, token: Optional[str] = None):
        """初始化GitHub服务"""
        self.token = token or settings.github_token
        self.github = Github(self.token) if self.token else None
        self.code_processor = CodeProcessor()
        
        # 支持的文件扩展名
        self.supported_extensions = {
            '.py': CodeLanguage.PYTHON,
            '.js': CodeLanguage.JAVASCRIPT,
            '.ts': CodeLanguage.TYPESCRIPT,
            '.java': CodeLanguage.JAVA,
            '.cpp': CodeLanguage.CPP,
            '.cc': CodeLanguage.CPP,
            '.cxx': CodeLanguage.CPP,
            '.go': CodeLanguage.GO,
            '.rs': CodeLanguage.RUST,
        }
    
    def parse_repository_url(self, url: str) -> Tuple[str, str]:
        """解析仓库URL，返回owner和repo_name"""
        try:
            # 处理各种URL格式
            if url.startswith('https://github.com/'):
                path = url.replace('https://github.com/', '').rstrip('/')
            elif url.startswith('git@github.com:'):
                path = url.replace('git@github.com:', '').replace('.git', '')
            else:
                # 假设是 "owner/repo" 格式
                path = url
            
            parts = path.split('/')
            if len(parts) >= 2:
                return parts[0], parts[1]
            else:
                raise ValueError(f"Invalid repository URL format: {url}")
        except Exception as e:
            raise ValueError(f"Failed to parse repository URL: {e}")
    
    def get_repository(self, owner: str, repo_name: str) -> Repository:
        """获取GitHub仓库对象"""
        if not self.github:
            raise ValueError("GitHub token not provided")
        
        try:
            repo = self.github.get_repo(f"{owner}/{repo_name}")
            return repo
        except GithubException as e:
            raise Exception(f"Failed to access repository {owner}/{repo_name}: {e}")
    
    def get_repository_info(self, owner: str, repo_name: str) -> Dict[str, Any]:
        """获取仓库基本信息"""
        repo = self.get_repository(owner, repo_name)
        
        return {
            "id": repo.id,
            "name": repo.name,
            "full_name": repo.full_name,
            "owner": repo.owner.login,
            "description": repo.description,
            "url": repo.html_url,
            "clone_url": repo.clone_url,
            "language": repo.language,
            "languages": list(repo.get_languages().keys()),
            "stars": repo.stargazers_count,
            "forks": repo.forks_count,
            "size": repo.size,
            "created_at": repo.created_at,
            "updated_at": repo.updated_at,
            "default_branch": repo.default_branch
        }
    
    def get_file_content(self, repo: Repository, file_path: str, branch: str = "main") -> Optional[str]:
        """获取文件内容"""
        try:
            # 尝试获取文件内容
            contents = repo.get_contents(file_path, ref=branch)
            
            if contents.type == "file":
                if contents.encoding == "base64":
                    content = base64.b64decode(contents.content).decode('utf-8')
                    return content
                else:
                    return contents.content
            else:
                return None
        except Exception as e:
            print(f"Error getting file content for {file_path}: {e}")
            return None
    
    def is_supported_file(self, file_path: str) -> bool:
        """检查文件是否被支持"""
        _, ext = os.path.splitext(file_path.lower())
        return ext in self.supported_extensions
    
    def should_skip_file(self, file_path: str) -> bool:
        """检查是否应该跳过文件"""
        # 跳过目录
        if file_path.endswith('/'):
            return True
        
        # 跳过二进制文件
        binary_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.pdf', '.zip', '.tar', '.gz'}
        _, ext = os.path.splitext(file_path.lower())
        if ext in binary_extensions:
            return True
        
        # 跳过测试文件（可选）
        skip_patterns = [
            'test/', 'tests/', '__pycache__/', '.git/', 'node_modules/',
            'venv/', 'env/', '.env', 'dist/', 'build/', 'target/'
        ]
        
        for pattern in skip_patterns:
            if pattern in file_path.lower():
                return True
        
        return False
    
    def get_repository_files(self, owner: str, repo_name: str, max_files: int = 100) -> List[Dict[str, Any]]:
        """获取仓库中的所有支持文件"""
        print(f"Getting files from repository: {owner}/{repo_name}")
        
        try:
            repo = self.get_repository(owner, repo_name)
            files = []
            
            # 获取默认分支
            default_branch = repo.default_branch
            print(f"Using default branch: {default_branch}")
            
            # 递归获取所有文件
            contents = repo.get_contents("", ref=default_branch)
            files_to_process = []
            
            print("Scanning repository structure...")
            # 使用队列进行广度优先搜索
            while contents and len(files_to_process) < max_files * 2:  # 获取更多文件以便过滤
                current_content = contents.pop(0)
                
                if current_content.type == "file":
                    if not self.should_skip_file(current_content.path) and self.is_supported_file(current_content.path):
                        files_to_process.append(current_content)
                        print(f"Found supported file: {current_content.path}")
                elif current_content.type == "dir":
                    # 获取目录内容
                    try:
                        dir_contents = repo.get_contents(current_content.path, ref=default_branch)
                        contents.extend(dir_contents)
                    except Exception as e:
                        print(f"Error accessing directory {current_content.path}: {e}")
            
            print(f"Found {len(files_to_process)} supported files, processing up to {max_files}...")
            
            # 处理文件内容
            processed_count = 0
            for content in files_to_process[:max_files]:
                try:
                    print(f"Getting content for: {content.path}")
                    file_content = self.get_file_content(repo, content.path, default_branch)
                    if file_content:
                        files.append({
                            "path": content.path,
                            "name": content.name,
                            "size": content.size,
                            "content": file_content,
                            "sha": content.sha,
                            "url": content.html_url
                        })
                        processed_count += 1
                        print(f"Successfully retrieved: {content.path} ({len(file_content)} chars)")
                    else:
                        print(f"No content retrieved for: {content.path}")
                except Exception as e:
                    print(f"Error processing file {content.path}: {e}")
                    continue
            
            print(f"Successfully processed {processed_count} files")
        
        except Exception as e:
            print(f"Error getting repository files: {e}")
            import traceback
            traceback.print_exc()
        
        return files
    
    def create_code_repository(self, owner: str, repo_name: str, max_files: int = 50) -> CodeRepository:
        """创建代码仓库对象"""
        print(f"Starting to process repository: {owner}/{repo_name}")
        
        try:
            # 获取仓库信息
            print("Step 1: Getting repository info...")
            repo_info = self.get_repository_info(owner, repo_name)
            print(f"Repository info retrieved: {repo_info['name']}")
            
            # 获取文件列表
            print(f"Step 2: Getting repository files (max: {max_files})...")
            files_data = self.get_repository_files(owner, repo_name, max_files)
            print(f"Found {len(files_data)} files to process")
            
            if not files_data:
                print("Warning: No files found to process")
                return CodeRepository(
                    id=f"repo_{repo_info['id']}",
                    name=repo_info["name"],
                    owner=repo_info["owner"],
                    url=repo_info["url"],
                    description=repo_info["description"],
                    total_files=0,
                    metadata=repo_info
                )
            
            # 创建代码仓库对象
            print("Step 3: Creating code repository object...")
            code_repo = CodeRepository(
                id=f"repo_{repo_info['id']}",
                name=repo_info["name"],
                owner=repo_info["owner"],
                url=repo_info["url"],
                description=repo_info["description"],
                total_files=len(files_data),
                metadata=repo_info
            )
            
            # 处理每个文件
            print("Step 4: Processing individual files...")
            total_lines = 0
            languages = set()
            processed_count = 0
            error_count = 0
            
            for i, file_data in enumerate(files_data):
                try:
                    print(f"Processing file {i+1}/{len(files_data)}: {file_data['path']}")
                    
                    # 创建代码文件对象
                    code_file = self.code_processor.process_file(
                        file_data["path"],
                        file_data["content"]
                    )
                    
                    # 更新文件元数据
                    code_file.metadata.update({
                        "github_url": file_data["url"],
                        "sha": file_data["sha"],
                        "size": file_data["size"]
                    })
                    
                    # 添加到仓库
                    code_repo.files.append(code_file)
                    languages.add(code_file.language)
                    total_lines += len(file_data["content"].split('\n'))
                    processed_count += 1
                    
                    print(f"Successfully processed: {file_data['path']} ({len(code_file.features)} features)")
                    
                except Exception as e:
                    error_count += 1
                    print(f"Error processing file {file_data['path']}: {e}")
                    print(f"File content length: {len(file_data.get('content', ''))}")
                    continue
            
            # 更新仓库统计信息
            print("Step 5: Updating repository statistics...")
            code_repo.languages = languages
            code_repo.total_lines = total_lines
            
            print(f"Repository processing completed:")
            print(f"  - Total files processed: {processed_count}")
            print(f"  - Files with errors: {error_count}")
            print(f"  - Total lines: {total_lines}")
            print(f"  - Languages: {list(languages)}")
            
            return code_repo
            
        except Exception as e:
            print(f"Critical error in create_code_repository: {e}")
            raise
    
    def search_repositories(self, query: str, language: Optional[str] = None, sort: str = "stars", order: str = "desc") -> List[Dict[str, Any]]:
        """搜索GitHub仓库"""
        if not self.github:
            raise ValueError("GitHub token not provided")
        
        try:
            # 构建搜索查询
            search_query = query
            if language:
                search_query += f" language:{language}"
            
            # 执行搜索
            repos = self.github.search_repositories(
                query=search_query,
                sort=sort,
                order=order
            )
            
            results = []
            for repo in repos[:20]:  # 限制结果数量
                results.append({
                    "name": repo.name,
                    "full_name": repo.full_name,
                    "owner": repo.owner.login,
                    "description": repo.description,
                    "url": repo.html_url,
                    "language": repo.language,
                    "stars": repo.stargazers_count,
                    "forks": repo.forks_count,
                    "updated_at": repo.updated_at
                })
            
            return results
        
        except Exception as e:
            raise Exception(f"Failed to search repositories: {e}")
    
    def get_repository_readme(self, owner: str, repo_name: str) -> Optional[str]:
        """获取仓库README内容"""
        try:
            repo = self.get_repository(owner, repo_name)
            
            # 尝试获取README文件
            readme_files = ["README.md", "README.rst", "README.txt", "README"]
            
            for readme_file in readme_files:
                try:
                    readme_content = repo.get_contents(readme_file)
                    if readme_content.encoding == "base64":
                        content = base64.b64decode(readme_content.content).decode('utf-8')
                        return content
                    else:
                        return readme_content.content
                except:
                    continue
            
            return None
        
        except Exception as e:
            print(f"Error getting README for {owner}/{repo_name}: {e}")
            return None


