"""
代码处理器 - 负责代码解析和特征提取
"""
import re
import os
from typing import List, Dict, Any, Optional, Set
from sentence_transformers import SentenceTransformer
import numpy as np

from ..models.code_model import CodeFile, CodeFeature, CodeRepository, CodeLanguage
from config import settings

class CodeProcessor:
    """代码处理器类"""
    
    def __init__(self):
        """初始化代码处理器"""
        self.embedding_model = SentenceTransformer(settings.embedding_model)
        self.parsers = {}
        self._initialize_parsers()
    
    def _initialize_parsers(self):
        """初始化各种语言的解析器"""
        # 暂时禁用tree-sitter，使用正则表达式解析
        print("Using regex-based parsing (tree-sitter disabled)")
        self.parsers = {}
    
    def detect_language(self, filename: str, content: str) -> CodeLanguage:
        """检测编程语言"""
        # 基于文件扩展名
        ext = os.path.splitext(filename)[1].lower()
        ext_mapping = {
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
        
        if ext in ext_mapping:
            return ext_mapping[ext]
        
        # 基于内容特征
        if 'def ' in content or 'import ' in content or 'class ' in content:
            return CodeLanguage.PYTHON
        elif 'function ' in content or 'const ' in content or 'let ' in content:
            return CodeLanguage.JAVASCRIPT
        elif 'public class' in content or 'private ' in content:
            return CodeLanguage.JAVA
        
        return CodeLanguage.PYTHON  # 默认
    
    def extract_functions(self, content: str, language: CodeLanguage) -> List[CodeFeature]:
        """提取函数"""
        functions = []
        
        # 尝试使用tree-sitter解析器
        if language in self.parsers:
            try:
                functions = self._extract_functions_with_tree_sitter(content, language)
                if functions:
                    return functions
            except Exception as e:
                print(f"Tree-sitter parsing failed for {language}: {e}")
                print("Falling back to regex-based parsing")
        
        # 回退到正则表达式解析
        if language == CodeLanguage.PYTHON:
            functions = self._extract_python_functions(content)
        elif language == CodeLanguage.JAVASCRIPT:
            functions = self._extract_javascript_functions(content)
        elif language == CodeLanguage.JAVA:
            functions = self._extract_java_functions(content)
        
        return functions
    
    def _extract_functions_with_tree_sitter(self, content: str, language: CodeLanguage) -> List[CodeFeature]:
        """使用tree-sitter提取函数"""
        functions = []
        
        try:
            parser = self.parsers[language]
            tree = parser.parse(bytes(content, "utf8"))
            
            # 根据语言类型提取函数节点
            if language == CodeLanguage.PYTHON:
                functions = self._extract_python_functions_tree_sitter(tree, content)
            elif language == CodeLanguage.JAVASCRIPT:
                functions = self._extract_javascript_functions_tree_sitter(tree, content)
            elif language == CodeLanguage.JAVA:
                functions = self._extract_java_functions_tree_sitter(tree, content)
                
        except Exception as e:
            print(f"Tree-sitter parsing error: {e}")
            
        return functions
    
    def _extract_python_functions_tree_sitter(self, tree, content: str) -> List[CodeFeature]:
        """使用tree-sitter提取Python函数"""
        functions = []
        lines = content.split('\n')
        
        def traverse(node):
            if node.type == 'function_definition':
                # 获取函数名
                name_node = node.child_by_field_name('name')
                if name_node:
                    func_name = content[name_node.start_byte:name_node.end_byte]
                    
                    # 获取函数体
                    func_content = content[node.start_byte:node.end_byte] 
                    func_lines = func_content.split('\n')
                    
                    # 计算行号
                    start_line = content[:node.start_byte].count('\n') + 1
                    end_line = content[:node.end_byte].count('\n') + 1
                    
                    feature = CodeFeature(
                        feature_type="function",
                        name=func_name,
                        content=func_content,
                        line_start=start_line,
                        line_end=end_line,
                        metadata={"language": "python", "parser": "tree_sitter"}
                    )
                    functions.append(feature)
            
            for child in node.children:
                traverse(child)
        
        traverse(tree.root_node)
        return functions
    
    def _extract_javascript_functions_tree_sitter(self, tree, content: str) -> List[CodeFeature]:
        """使用tree-sitter提取JavaScript函数"""
        functions = []
        
        def traverse(node):
            if node.type in ['function_declaration', 'function_expression', 'arrow_function']:
                # 获取函数名
                name_node = node.child_by_field_name('name')
                func_name = "anonymous"
                if name_node:
                    func_name = content[name_node.start_byte:name_node.end_byte]
                
                # 获取函数体
                func_content = content[node.start_byte:node.end_byte]
                start_line = content[:node.start_byte].count('\n') + 1
                end_line = content[:node.end_byte].count('\n') + 1
                
                feature = CodeFeature(
                    feature_type="function",
                    name=func_name,
                    content=func_content,
                    line_start=start_line,
                    line_end=end_line,
                    metadata={"language": "javascript", "parser": "tree_sitter"}
                )
                functions.append(feature)
            
            for child in node.children:
                traverse(child)
        
        traverse(tree.root_node)
        return functions
    
    def _extract_java_functions_tree_sitter(self, tree, content: str) -> List[CodeFeature]:
        """使用tree-sitter提取Java方法"""
        functions = []
        
        def traverse(node):
            if node.type == 'method_declaration':
                # 获取方法名
                name_node = node.child_by_field_name('name')
                if name_node:
                    method_name = content[name_node.start_byte:name_node.end_byte]
                    
                    # 获取方法体
                    method_content = content[node.start_byte:node.end_byte]
                    start_line = content[:node.start_byte].count('\n') + 1
                    end_line = content[:node.end_byte].count('\n') + 1
                    
                    feature = CodeFeature(
                        feature_type="function",
                        name=method_name,
                        content=method_content,
                        line_start=start_line,
                        line_end=end_line,
                        metadata={"language": "java", "parser": "tree_sitter"}
                    )
                    functions.append(feature)
            
            for child in node.children:
                traverse(child)
        
        traverse(tree.root_node)
        return functions
    
    def _extract_python_functions(self, content: str) -> List[CodeFeature]:
        """提取Python函数"""
        functions = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            # 匹配函数定义
            func_match = re.match(r'def\s+(\w+)\s*\([^)]*\):', line)
            if func_match:
                func_name = func_match.group(1)
                
                # 找到函数体结束位置
                end_line = i
                indent_level = len(line) - len(line.lstrip())
                
                for j in range(i + 1, len(lines)):
                    if lines[j].strip() and not lines[j].startswith('#'):
                        current_indent = len(lines[j]) - len(lines[j].lstrip())
                        if current_indent <= indent_level:
                            end_line = j
                            break
                    end_line = j
                
                func_content = '\n'.join(lines[i:end_line])
                feature = CodeFeature(
                    feature_type="function",
                    name=func_name,
                    content=func_content,
                    line_start=i + 1,
                    line_end=end_line,
                    metadata={"language": "python"}
                )
                functions.append(feature)
        
        return functions
    
    def _extract_javascript_functions(self, content: str) -> List[CodeFeature]:
        """提取JavaScript函数"""
        functions = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            # 匹配各种函数定义
            patterns = [
                r'function\s+(\w+)\s*\([^)]*\)',
                r'const\s+(\w+)\s*=\s*\([^)]*\)\s*=>',
                r'(\w+)\s*:\s*function\s*\([^)]*\)',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, line)
                if match:
                    func_name = match.group(1)
                    func_content = line.strip()
                    
                    feature = CodeFeature(
                        feature_type="function",
                        name=func_name,
                        content=func_content,
                        line_start=i + 1,
                        line_end=i + 1,
                        metadata={"language": "javascript"}
                    )
                    functions.append(feature)
        
        return functions
    
    def _extract_java_functions(self, content: str) -> List[CodeFeature]:
        """提取Java方法"""
        functions = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            # 匹配方法定义
            method_match = re.match(r'\s*(public|private|protected)?\s*(static)?\s*\w+\s+(\w+)\s*\([^)]*\)', line)
            if method_match:
                method_name = method_match.group(3)
                
                # 找到方法体结束位置（简单实现）
                brace_count = 0
                end_line = i
                for j in range(i, len(lines)):
                    brace_count += lines[j].count('{') - lines[j].count('}')
                    if brace_count == 0 and j > i:
                        end_line = j
                        break
                
                method_content = '\n'.join(lines[i:end_line + 1])
                feature = CodeFeature(
                    feature_type="function",
                    name=method_name,
                    content=method_content,
                    line_start=i + 1,
                    line_end=end_line + 1,
                    metadata={"language": "java"}
                )
                functions.append(feature)
        
        return functions
    
    def extract_classes(self, content: str, language: CodeLanguage) -> List[CodeFeature]:
        """提取类定义"""
        classes = []
        
        if language == CodeLanguage.PYTHON:
            classes = self._extract_python_classes(content)
        elif language == CodeLanguage.JAVA:
            classes = self._extract_java_classes(content)
        elif language == CodeLanguage.JAVASCRIPT:
            classes = self._extract_javascript_classes(content)
        
        return classes
    
    def _extract_python_classes(self, content: str) -> List[CodeFeature]:
        """提取Python类"""
        classes = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            class_match = re.match(r'class\s+(\w+)', line)
            if class_match:
                class_name = class_match.group(1)
                
                # 找到类体结束位置
                end_line = i
                indent_level = len(line) - len(line.lstrip())
                
                for j in range(i + 1, len(lines)):
                    if lines[j].strip() and not lines[j].startswith('#'):
                        current_indent = len(lines[j]) - len(lines[j].lstrip())
                        if current_indent <= indent_level:
                            end_line = j
                            break
                    end_line = j
                
                class_content = '\n'.join(lines[i:end_line])
                feature = CodeFeature(
                    feature_type="class",
                    name=class_name,
                    content=class_content,
                    line_start=i + 1,
                    line_end=end_line,
                    metadata={"language": "python"}
                )
                classes.append(feature)
        
        return classes
    
    def _extract_java_classes(self, content: str) -> List[CodeFeature]:
        """提取Java类"""
        classes = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            class_match = re.match(r'\s*(public|private|protected)?\s*class\s+(\w+)', line)
            if class_match:
                class_name = class_match.group(2)
                
                # 找到类体结束位置
                brace_count = 0
                end_line = i
                for j in range(i, len(lines)):
                    brace_count += lines[j].count('{') - lines[j].count('}')
                    if brace_count == 0 and j > i:
                        end_line = j
                        break
                
                class_content = '\n'.join(lines[i:end_line + 1])
                feature = CodeFeature(
                    feature_type="class",
                    name=class_name,
                    content=class_content,
                    line_start=i + 1,
                    line_end=end_line + 1,
                    metadata={"language": "java"}
                )
                classes.append(feature)
        
        return classes
    
    def _extract_javascript_classes(self, content: str) -> List[CodeFeature]:
        """提取JavaScript类"""
        classes = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            class_match = re.search(r'class\s+(\w+)', line)
            if class_match:
                class_name = class_match.group(1)
                
                # 找到类体结束位置
                brace_count = 0
                end_line = i
                for j in range(i, len(lines)):
                    brace_count += lines[j].count('{') - lines[j].count('}')
                    if brace_count == 0 and j > i:
                        end_line = j
                        break
                
                class_content = '\n'.join(lines[i:end_line + 1])
                feature = CodeFeature(
                    feature_type="class",
                    name=class_name,
                    content=class_content,
                    line_start=i + 1,
                    line_end=end_line + 1,
                    metadata={"language": "javascript"}
                )
                classes.append(feature)
        
        return classes
    
    def extract_imports(self, content: str, language: CodeLanguage) -> List[CodeFeature]:
        """提取导入语句"""
        imports = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            if language == CodeLanguage.PYTHON:
                if re.match(r'import\s+\w+|from\s+\w+\s+import', line):
                    feature = CodeFeature(
                        feature_type="import",
                        name="import",
                        content=line.strip(),
                        line_start=i + 1,
                        line_end=i + 1,
                        metadata={"language": "python"}
                    )
                    imports.append(feature)
            
            elif language == CodeLanguage.JAVASCRIPT:
                if re.match(r'import\s+.*from\s+.*|require\s*\(', line):
                    feature = CodeFeature(
                        feature_type="import",
                        name="import",
                        content=line.strip(),
                        line_start=i + 1,
                        line_end=i + 1,
                        metadata={"language": "javascript"}
                    )
                    imports.append(feature)
            
            elif language == CodeLanguage.JAVA:
                if re.match(r'import\s+\w+', line):
                    feature = CodeFeature(
                        feature_type="import",
                        name="import",
                        content=line.strip(),
                        line_start=i + 1,
                        line_end=i + 1,
                        metadata={"language": "java"}
                    )
                    imports.append(feature)
        
        return imports
    
    def extract_comments(self, content: str, language: CodeLanguage) -> List[CodeFeature]:
        """提取注释"""
        comments = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            comment_content = None
            
            if language == CodeLanguage.PYTHON:
                if line.strip().startswith('#'):
                    comment_content = line.strip()
            elif language in [CodeLanguage.JAVASCRIPT, CodeLanguage.JAVA]:
                if '//' in line:
                    comment_content = line.split('//')[1].strip()
                elif '/*' in line and '*/' in line:
                    comment_content = line.strip()
            
            if comment_content and len(comment_content) > 5:
                feature = CodeFeature(
                    feature_type="comment",
                    name="comment",
                    content=comment_content,
                    line_start=i + 1,
                    line_end=i + 1,
                    metadata={"language": language.value}
                )
                comments.append(feature)
        
        return comments
    
    def extract_features(self, content: str, language: CodeLanguage) -> List[CodeFeature]:
        """提取所有代码特征"""
        features = []
        
        # 提取各种特征
        features.extend(self.extract_functions(content, language)) 
        features.extend(self.extract_classes(content, language))
        features.extend(self.extract_imports(content, language))
        features.extend(self.extract_comments(content, language))
        
        return features
    
    def generate_embeddings(self, features: List[CodeFeature]) -> List[CodeFeature]:
        """为代码特征生成嵌入向量"""
        texts = []
        for feature in features:
            # 组合特征名称和内容
            combined_text = f"{feature.name}: {feature.content}"
            texts.append(combined_text)
        
        if not texts:
            return features
        
        # 生成嵌入向量
        embeddings = self.embedding_model.encode(texts)
        
        # 更新特征
        for i, feature in enumerate(features):
            feature.embedding = embeddings[i].tolist()
        
        return features
    
    def process_file(self, file_path: str, content: str) -> CodeFile:
        """处理代码文件"""
        filename = os.path.basename(file_path)
        language = self.detect_language(filename, content)
        
        # 创建代码文件对象
        code_file = CodeFile(
            id=f"file_{hash(file_path)}",
            filename=filename,
            filepath=file_path,
            language=language,
            content=content,
            size=len(content.encode('utf-8'))
        )
        
        # 提取特征
        features = self.extract_features(content, language)
        
        # 生成嵌入向量
        features = self.generate_embeddings(features)
        
        # 分类特征
        functions = [f for f in features if f.feature_type == "function"]
        classes = [f for f in features if f.feature_type == "class"]
        imports = [f for f in features if f.feature_type == "import"]
        comments = [f for f in features if f.feature_type == "comment"]
        
        # 更新文件对象
        code_file.features = features
        code_file.functions = functions
        code_file.classes = classes
        code_file.imports = imports
        code_file.comments = comments
        
        return code_file
    
    def calculate_similarity(self, code1: str, code2: str) -> float:
        """计算两个代码片段的相似度"""
        embeddings = self.embedding_model.encode([code1, code2])
        similarity = np.dot(embeddings[0], embeddings[1]) / (
            np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
        )
        return float(similarity)


