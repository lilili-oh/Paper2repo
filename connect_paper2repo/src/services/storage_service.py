"""
存储服务 - 负责数据持久化
"""
import os
import json
import pickle
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from datetime import datetime

from ..models.text_model import TextDocument
from ..models.code_model import CodeRepository
from ..models.alignment_model import AlignmentResult
from config import settings


class StorageService:
    """存储服务类"""
    
    def __init__(self):
        """初始化存储服务"""
        self.chroma_client = None
        self.text_collection = None
        self.code_collection = None
        self.alignment_collection = None
        self._initialize_chroma()
    
    def _initialize_chroma(self):
        """初始化ChromaDB"""
        try:
            # 确保数据目录存在
            os.makedirs(settings.chroma_persist_directory, exist_ok=True)
            
            # 初始化ChromaDB客户端
            self.chroma_client = chromadb.PersistentClient(
                path=settings.chroma_persist_directory,
                settings=ChromaSettings(
                    anonymized_telemetry=False
                )
            )
            
            # 创建或获取集合
            self.text_collection = self.chroma_client.get_or_create_collection(
                name="text_documents",
                # metadata={"description": "Text documents and features"},
                # embedding_function=DummyEmbedding()
            )
                # 测试添加数据以验证连接
              
            # 获取或创建其他集合        
            self.code_collection = self.chroma_client.get_or_create_collection(
                name="code_repositories", 
                metadata={"description": "Code repositories and features"}
            )
            
            self.alignment_collection = self.chroma_client.get_or_create_collection(
                name="alignment_results",
                metadata={"description": "Alignment results between text and code"}
            )
            
            print("ChromaDB initialized successfully")
            
        except Exception as e:
            print(f"Warning: Could not initialize ChromaDB: {e}")
            print("Falling back to file-based storage")
            # 确保数据目录存在
            os.makedirs("data", exist_ok=True)
            os.makedirs("data/text_documents", exist_ok=True)
            os.makedirs("data/code_repositories", exist_ok=True)
            os.makedirs("data/alignment_results", exist_ok=True)
    def save_text_document(self, document: TextDocument) -> bool:
        """保存文本文档（带详细调试信息）"""
        try:
            print("\n========== [DEBUG] save_text_document START ==========")
            print(f"document.id = {document.id}")
            print(f"document.title = {getattr(document, 'title', None)}")
            print(f"document.language = {getattr(document, 'language', None)}")
            print(f"document.features count = {len(getattr(document, 'features', []))}")

            # 检查 collection 是否存在
            print(f"self.text_collection is : {self.text_collection}")
            if self.text_collection:
                print("[1] ✅ 开始保存到 ChromaDB")

                documents, metadatas, ids = [], [], []

                # 添加主文档
                try:
                    documents.append(document.content)
                    metadatas.append({
                        "type": "document",
                        "title": document.title,
                        "source": document.source,
                        "language": document.language,
                        "created_at": document.created_at.isoformat(),
                        "feature_count": len(document.features)
                    })
                    ids.append(document.id)
                    print(f"[2] 已添加主文档 id={document.id}")
                except Exception as e:
                    print(f"[❌] 添加主文档失败: {e}")

                # 添加特征
                counter = 0
                for feature in getattr(document, "features", []):
                    try:
                        if feature.embedding:
                            documents.append(feature.content)
                            metadatas.append({
                                "type": "feature",
                                "feature_type": feature.feature_type,
                                "position": feature.position,
                                "document_id": document.id,
                                "parent_type": "document"
                            })
                            ids.append(f"{document.id}_feature_{feature.position}_{counter}")
                            counter += 1
                    except Exception as fe:
                        print(f"[❌] 添加特征失败: {fe}")

                print(f"[3] documents={len(documents)}, metadatas={len(metadatas)}, ids={len(ids)}")

                # 批量添加
                # try:
                #     self.text_collection.add(
                #         documents=documents,
                #         metadatas=metadatas,
                #         ids=ids
                #     )
                #     print("[4] ✅ 成功保存到 ChromaDB")
                # except Exception as e:
                #     print(f"[❌] 批量添加到 ChromaDB 失败: {e}")

            else:
                print("[⚠️] self.text_collection 为空，跳过 ChromaDB 保存")

            # 文件备份部分
            try:
                print("[5] 开始保存文件到本地备份...")
                self._save_to_file(f"text_documents/{document.id}.json", document.dict())
                print("[6] ✅ 文件备份成功")
            except Exception as e:
                print(f"[❌] 文件保存失败: {e}")

            print("========== [DEBUG] save_text_document END ==========\n")
            return True

        except Exception as e:
            import traceback
            print(f"[❌] save_text_document 外层异常: {e}")
            traceback.print_exc()
            return False
    
    # def save_text_document(self, document: TextDocument) -> bool:
    #     """保存文本文档"""
    #     try:
    #         # 保存到ChromaDB
    #         print(f"self.text_collection is : {self.text_collection}")
    #         if self.text_collection:
    #             print("start save text document to chromadb")
    #             # 准备文档数据
    #             documents = []
    #             metadatas = []
    #             ids = []
                
    #             # 添加主文档
    #             documents.append(document.content)
    #             metadatas.append({
    #                 "type": "document",
    #                 "title": document.title,
    #                 "source": document.source,
    #                 "language": document.language,
    #                 "created_at": document.created_at.isoformat(),
    #                 "feature_count": len(document.features)
    #             })
    #             ids.append(document.id)
                
    #             # 添加特征
    #             counter = 0
    #             for feature in document.features:
    #                 if feature.embedding:
    #                     documents.append(feature.content)
    #                     metadatas.append({
    #                         "type": "feature",
    #                         "feature_type": feature.feature_type,
    #                         "position": feature.position,
    #                         "document_id": document.id,
    #                         "parent_type": "document"
    #                     })
    #                     ids.append(f"{document.id}_feature_{feature.position}_{counter}")
    #                     counter += 1
                
    #             # 批量添加到集合
    #             self.text_collection.add(
    #                 documents=documents,
    #                 metadatas=metadatas,
    #                 ids=ids
    #             )
    #             print("save text document to chromadb success")
    #         # 同时保存到文件系统作为备份
    #         self._save_to_file(f"text_documents/{document.id}.json", document.dict())
    #         print("save text document success")
    #         return True
            
    #     except Exception as e:
    #         print(f"Error saving text document: {e}")
    #         return False
    
    def save_code_repository(self, repository: CodeRepository) -> bool:
        """保存代码仓库"""
        try:
            # 保存到ChromaDB
            if self.code_collection:
                # 准备仓库数据
                documents = []
                metadatas = []
                ids = []
                
                # 添加仓库信息
                documents.append(repository.description or "")
                metadatas.append({
                    "type": "repository",
                    "name": repository.name,
                    "owner": repository.owner,
                    "url": repository.url,
                    "total_files": repository.total_files,
                    "total_lines": repository.total_lines,
                    "languages": list(repository.languages),
                    "created_at": repository.created_at.isoformat()
                })
                ids.append(repository.id)
                
                # 添加文件特征
                for file in repository.files:
                    for feature in file.features:
                        if feature.embedding:
                            documents.append(feature.content)
                            metadatas.append({
                                "type": "feature",
                                "feature_type": feature.feature_type,
                                "name": feature.name,
                                "language": file.language.value,
                                "filepath": file.filepath,
                                "line_start": feature.line_start,
                                "line_end": feature.line_end,
                                "repository_id": repository.id,
                                "file_id": file.id,
                                "parent_type": "code"
                            })
                            ids.append(f"{repository.id}_{file.id}_{feature.name}_{feature.line_start}")
                
                # # 批量添加到集合
                # self.code_collection.add(
                #     documents=documents,
                #     metadatas=metadatas,
                #     ids=ids
                # )
            
            # 同时保存到文件系统作为备份
            self._save_to_file(f"code_repositories/{repository.id}.json", repository.dict())
            
            return True
            
        except Exception as e:
            print(f"Error saving code repository: {e}")
            return False
    
    def save_alignment_result(self, alignment: AlignmentResult) -> bool:
        """保存对齐结果"""
        try:
            # 保存到ChromaDB
            if self.alignment_collection:
                # 准备对齐数据
                documents = []
                metadatas = []
                ids = []
                
                # 添加对齐结果摘要
                summary = f"Alignment between {alignment.text_document_id} and {alignment.code_repository_id}"
                documents.append(summary)
                metadatas.append({
                    "type": "alignment",
                    "text_document_id": alignment.text_document_id,
                    "code_repository_id": alignment.code_repository_id,
                    "total_matches": alignment.total_matches,
                    "average_similarity": alignment.average_similarity,
                    "alignment_coverage": alignment.alignment_coverage,
                    "processing_time": alignment.processing_time,
                    "created_at": alignment.created_at.isoformat()
                })
                ids.append(alignment.id)
                
                # 添加匹配详情
                for i, match in enumerate(alignment.matches[:50]):  # 限制数量
                    documents.append(f"{match.text_feature} -> {match.code_feature}")
                    metadatas.append({
                        "type": "match",
                        "alignment_id": alignment.id,
                        "similarity_score": match.similarity_score.score,
                        "alignment_type": match.alignment_type.value,
                        "match_index": i,
                        "parent_type": "alignment"
                    })
                    ids.append(f"{alignment.id}_match_{i}")
                
                # 批量添加到集合
                # self.alignment_collection.add(
                #     documents=documents,
                #     metadatas=metadatas,
                #     ids=ids
                # )
            
            # 同时保存到文件系统作为备份
            self._save_to_file(f"alignment_results/{alignment.id}.json", alignment.dict())
            
            return True
            
        except Exception as e:
            print(f"Error saving alignment result: {e}")
            return False
    
    def load_text_document(self, document_id: str) -> Optional[TextDocument]:
        """加载文本文档"""
        try:
            # 从文件系统加载
            file_path = f"data/text_documents/{document_id}.json"
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return TextDocument(**data)
            
            return None
            
        except Exception as e:
            print(f"Error loading text document: {e}")
            return None
    
    def load_code_repository(self, repository_id: str) -> Optional[CodeRepository]:
        """加载代码仓库"""
        try:
            # 从文件系统加载
            file_path = f"data/code_repositories/{repository_id}.json"
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return CodeRepository(**data)
            
            return None
            
        except Exception as e:
            print(f"Error loading code repository: {e}")
            return None
    
    def load_alignment_result(self, alignment_id: str) -> Optional[AlignmentResult]:
        """加载对齐结果"""
        try:
            # 从文件系统加载
            file_path = f"data/alignment_results/{alignment_id}.json"
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return AlignmentResult(**data)
            
            return None
            
        except Exception as e:
            print(f"Error loading alignment result: {e}")
            return None
    
    def search_similar_text(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """搜索相似文本"""
        try:
            if not self.text_collection:
                return []
            
            results = self.text_collection.query(
                query_texts=[query],
                n_results=top_k
            )
            
            return self._format_search_results(results)
            
        except Exception as e:
            print(f"Error searching similar text: {e}")
            return []
    
    def search_similar_code(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """搜索相似代码"""
        try:
            if not self.code_collection:
                return []
            
            results = self.code_collection.query(
                query_texts=[query],
                n_results=top_k
            )
            
            return self._format_search_results(results)
            
        except Exception as e:
            print(f"Error searching similar code: {e}")
            return []
    
    def _format_search_results(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """格式化搜索结果"""
        formatted_results = []
        
        if 'documents' in results and results['documents']:
            for i, doc in enumerate(results['documents'][0]):
                formatted_results.append({
                    "content": doc,
                    "metadata": results['metadatas'][0][i] if 'metadatas' in results else {},
                    "distance": results['distances'][0][i] if 'distances' in results else 0.0
                })
        
        return formatted_results
    
    def _save_to_file(self, file_path: str, data: Dict[str, Any]) -> bool:
        """保存数据到文件"""
        # try:
        #     # 确保目录存在
        #     os.makedirs(os.path.dirname(f"data/{file_path}"), exist_ok=True)
            
        #     # 保存JSON文件
        #     print(f"Saving data to file: data/{file_path}")
        #     with open(f"data/{file_path}", 'w', encoding='utf-8') as f:
        #         json.dump(data, f, ensure_ascii=False, indent=2, default=str)
            
        #     return True
            
        # except Exception as e:
        #     print(f"Error saving to file {file_path}: {e}")
        #     return False
        full_path = os.path.join("data", file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        try:
            with open(full_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
            print(f"[✅] 文件已保存到 {full_path}")
        except Exception as e:
            print(f"[❌] 保存文件 {full_path} 失败：{e}")
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """获取存储统计信息"""
        stats = {
            "text_documents": 0,
            "code_repositories": 0,
            "alignment_results": 0,
            "total_size": 0
        }
        
        try:
            # 统计文件数量
            data_dir = "data"
            if os.path.exists(data_dir):
                for root, dirs, files in os.walk(data_dir):
                    for file in files:
                        if file.endswith('.json'):
                            file_path = os.path.join(root, file)
                            stats["total_size"] += os.path.getsize(file_path)
                            
                            if 'text_documents' in file_path:
                                stats["text_documents"] += 1
                            elif 'code_repositories' in file_path:
                                stats["code_repositories"] += 1
                            elif 'alignment_results' in file_path:
                                stats["alignment_results"] += 1
            
            # 获取ChromaDB统计
            if self.text_collection:
                stats["text_collection_count"] = self.text_collection.count()
            if self.code_collection:
                stats["code_collection_count"] = self.code_collection.count()
            if self.alignment_collection:
                stats["alignment_collection_count"] = self.alignment_collection.count()
        
        except Exception as e:
            print(f"Error getting storage stats: {e}")
        
        return stats


