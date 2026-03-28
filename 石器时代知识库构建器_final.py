#!/usr/bin/env python3
"""
石器时代知识库构建器 v2.0
从已有的脚本文件中提取关键信息，构建结构化知识库
"""

import os
import re
import json
import time
from pathlib import Path

class StoneAgeKnowledgeBuilder:
    def __init__(self):
        self.workspace_dir = "/root/.openclaw/workspace"
        self.knowledge_dir = os.path.join(self.workspace_dir, "石器时代知识库_v2")
        self.ensure_directories()
        
        # 数据存储
        self.knowledge_base = {
            "metadata": {
                "name": "石器时代游戏知识库 v2.0",
                "version": "2.0.0",
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "description": "从脚本文件中提取的石器时代游戏知识"
            },
            "maps": [],      # 地图信息
            "npcs": [],      # NPC信息
            "pets": [],      # 宠物信息
            "coordinates": [], # 坐标信息
            "items": [],     # 物品信息
            "skills": [],    # 技能信息
            "scripts": []    # 脚本信息
        }
    
    def ensure_directories(self):
        """确保目录结构存在"""
        directories = [
            self.knowledge_dir,
            os.path.join(self.knowledge_dir, "原始脚本"),
            os.path.join(self.knowledge_dir, "分析结果"),
            os.path.join(self.knowledge_dir, "知识图谱"),
            os.path.join(self.knowledge_dir, "NG25适配"),
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            print(f"✅ 目录已创建: {directory}")
    
    def find_script_files(self):
        """查找所有石器时代脚本文件"""
        script_files = []
        
        # 搜索.asc文件
        for root, dirs, files in os.walk(self.workspace_dir):
            for file in files:
                if file.endswith('.asc'):
                    script_files.append(os.path.join(root, file))
                elif '石器' in file or '脚本' in file or 'NG25' in file:
                    script_files.append(os.path.join(root, file))
        
        print(f"📁 找到 {len(script_files)} 个脚本文件")
        return script_files
    
    def analyze_script_file(self, filepath):
        """分析单个脚本文件"""
        print(f"🔍 分析文件: {os.path.basename(filepath)}")
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 复制到知识库
            filename = os.path.basename(filepath)
            dest_path = os.path.join(self.knowledge_dir, "原始脚本", filename)
            with open(dest_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # 提取信息
            extracted = {
                "file": filename,
                "size": len(content),
                "lines": content.count('\n') + 1,
                "maps": self.extract_maps(content),
                "npcs": self.extract_npcs(content),
                "pets": self.extract_pets(content),
                "coordinates": self.extract_coordinates(content),
                "items": self.extract_items(content),
                "commands": self.extract_commands(content)
            }
            
            return extracted
            
        except Exception as e:
            print(f"❌ 分析文件失败 {filepath}: {e}")
            return None
    
    def extract_maps(self, content):
        """提取地图信息"""
        maps = []
        
        # 地图ID模式
        patterns = [
            r'map\s*[=:]\s*(\d+)',  # map=1001
            r'地图\s*[=:]\s*(\d+)',  # 地图=1001
            r'(\d{3,4})\s*地图',     # 1001地图
            r'地图(\d{3,4})',        # 地图1001
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if match not in maps:
                    maps.append(match)
        
        return maps
    
    def extract_npcs(self, content):
        """提取NPC信息"""
        npcs = []
        
        # NPC名称模式
        patterns = [
            r'NPC\s*[=:]\s*([^\s\n,;]{2,20})',  # NPC=村长
            r'对话\s*[=:]\s*([^\s\n,;]{2,20})',  # 对话=村长
            r'找\s*([^\s\n,;]{2,20})\s*NPC',    # 找村长NPC
            r'([^\s\n,;]{2,20})\s*NPC',         # 村长NPC
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if match not in npcs and len(match) > 1:
                    npcs.append(match)
        
        return npcs
    
    def extract_pets(self, content):
        """提取宠物信息"""
        pets = []
        
        # 宠物名称模式
        patterns = [
            r'宠物\s*[=:]\s*([^\s\n,;]{2,20})',  # 宠物=雷龙
            r'宠\s*[=:]\s*([^\s\n,;]{2,20})',    # 宠=雷龙
            r'([^\s\n,;]{2,20})\s*宠',           # 雷龙宠
            r'培养\s*([^\s\n,;]{2,20})',         # 培养雷龙
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if match not in pets and len(match) > 1:
                    pets.append(match)
        
        return pets
    
    def extract_coordinates(self, content):
        """提取坐标信息"""
        coordinates = []
        
        # 坐标模式
        patterns = [
            r'坐标\s*[=:]\s*(\d+)[,\s]+(\d+)',  # 坐标=100,200
            r'\((\d+)[,\s]+(\d+)\)',           # (100,200)
            r'(\d+)[,\s]+(\d+)\s*坐标',        # 100,200坐标
            r'走到\s*(\d+)[,\s]+(\d+)',        # 走到100,200
            r'移动到\s*(\d+)[,\s]+(\d+)',      # 移动到100,200
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if len(match) == 2:
                    coord = f"{match[0]},{match[1]}"
                    if coord not in coordinates:
                        coordinates.append(coord)
        
        return coordinates
    
    def extract_items(self, content):
        """提取物品信息"""
        items = []
        
        # 物品名称模式
        patterns = [
            r'物品\s*[=:]\s*([^\s\n,;]{2,20})',  # 物品=石头
            r'道具\s*[=:]\s*([^\s\n,;]{2,20})',  # 道具=石头
            r'获得\s*([^\s\n,;]{2,20})',         # 获得石头
            r'使用\s*([^\s\n,;]{2,20})',         # 使用石头
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if match not in items and len(match) > 1:
                    items.append(match)
        
        return items
    
    def extract_commands(self, content):
        """提取ASSA命令"""
        commands = []
        
        # ASSA命令模式
        patterns = [
            r'let\s+@[^\s=]+\s*=',          # let @变量=
            r'waitmap\s+[^\s\n]+',          # waitmap 地图
            r'walk\s+[^\s\n]+',             # walk 坐标
            r'say\s+[^\s\n]+',              # say 文本
            r'button\s+[^\s\n]+',           # button 按钮
            r'dlg\s+[^\s\n]+',              # dlg 对话框
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if match not in commands:
                    commands.append(match.strip())
        
        return commands
    
    def build_knowledge_base(self):
        """构建知识库"""
        print("="*60)
        print("🧠 开始构建石器时代知识库 v2.0")
        print("="*60)
        
        # 查找脚本文件
        script_files = self.find_script_files()
        
        all_analysis = []
        
        for filepath in script_files[:10]:  # 只分析前10个文件，避免太多
            analysis = self.analyze_script_file(filepath)
            if analysis:
                all_analysis.append(analysis)
                
                # 合并到知识库
                self.knowledge_base["maps"].extend(analysis["maps"])
                self.knowledge_base["npcs"].extend(analysis["npcs"])
                self.knowledge_base["pets"].extend(analysis["pets"])
                self.knowledge_base["coordinates"].extend(analysis["coordinates"])
                self.knowledge_base["items"].extend(analysis["items"])
                
                # 添加脚本信息
                script_info = {
                    "name": analysis["file"],
                    "size": analysis["size"],
                    "lines": analysis["lines"],
                    "commands_count": len(analysis["commands"]),
                    "commands_sample": analysis["commands"][:5] if analysis["commands"] else []
                }
                self.knowledge_base["scripts"].append(script_info)
        
        # 去重
        for key in ["maps", "npcs", "pets", "coordinates", "items"]:
            self.knowledge_base[key] = list(set(self.knowledge_base[key]))
        
        # 保存知识库
        self.save_knowledge_base()
        
        # 生成分析报告
        self.generate_analysis_report(all_analysis)
        
        # 创建知识图谱
        self.create_knowledge_graph()
        
        # 创建NG25适配器
        self.create_ng25_adapter()
        
        return self.knowledge_base
    
    def save_knowledge_base(self):
        """保存知识库到文件"""
        # JSON格式
        json_file = os.path.join(self.knowledge_dir, "知识库.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.knowledge_base, f, ensure_ascii=False, indent=2)
        
        # Markdown格式
        md_file = os.path.join(self.knowledge_dir, "知识库.md")
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write("# 石器时代游戏知识库 v2.0\n\n")
            f.write(f"**生成时间**: {self.knowledge_base['metadata']['created_at']}\n\n")
            
            f.write("## 数据统计\n\n")
            f.write(f"- **地图数量**: {len(self.knowledge_base['maps'])}\n")
            f.write(f"- **NPC数量**: {len(self.knowledge_base['npcs'])}\n")
            f.write(f"- **宠物数量**: {len(self.knowledge_base['pets'])}\n")
            f.write(f"- **坐标数量**: {len(self.knowledge_base['coordinates'])}\n")
            f.write(f"- **物品数量**: {len(self.knowledge_base['items'])}\n")
            f.write(f"- **脚本数量**: {len(self.knowledge_base['scripts'])}\n\n")
            
            f.write("## 地图列表\n\n")
            for i, map_id in enumerate(sorted(self.knowledge_base['maps']), 1):
                f.write(f"{i}. 地图ID: {map_id}\n")
            
            f.write("\n## NPC列表\n\n")
            for i, npc in enumerate(sorted(self.knowledge_base['npcs']), 1):
                f.write(f"{i}. {npc}\n")
            
            f.write("\n## 宠物列表\n\n")
            for i, pet in enumerate(sorted(self.knowledge_base['pets']), 1):
                f.write(f"{i}. {pet}\n")
            
            f.write("\n## 坐标列表\n\n")
            for i, coord in enumerate(sorted(self.knowledge_base['coordinates']), 1):
                f.write(f"{i}. {coord}\n")
            
            f.write("\n## 物品列表\n\n")
            for i, item in enumerate(sorted(self.knowledge_base['items']), 1):
                f.write(f"{i}. {item}\n")
            
            f.write("\n## 脚本列表\n\n")
            for i, script in enumerate(self.knowledge_base['scripts'], 1):
                f.write(f"{i}. **{script['name']}**\n")
                f.write(f"   - 大小: {script['size']} 字节\n")
                f.write(f"   - 行数: {script['lines']} 行\n")
                f.write(f"   - 命令数: {script['commands_count']} 个\n")
                if script['commands_sample']:
                    f.write(f"   - 命令示例: {', '.join(script['commands_sample'])}\n")
        
        print(f"✅ 知识库已保存:")
        print(f"   📄 JSON格式: {json_file}")
        print(f"   📄 Markdown格式: {md_file}")
    
    def generate_analysis_report(self, all_analysis):
        """生成分析报告"""
        report_file = os.path.join(self.knowledge_dir, "分析结果", "脚本分析报告.md")
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# 石器时代脚本分析报告 v2.0\n\n")
            f.write(f"**分析时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**分析文件数**: {len(all_analysis)}\n\n")
            
            f.write("## 文件分析详情\n\n")
            
            total_size = 0
            total_lines = 0
            
            for analysis in all_analysis:
                f.write(f"### {analysis['file']}\n")
                f.write(f"- **大小**: {analysis['size']} 字节\n")
                f.write(f"- **行数**: {analysis['lines']} 行\n")
                
                total_size += analysis['size']
                total_lines += analysis['lines']
                
                # 各类型数据统计
                f.write(f"- **地图ID**: {len(analysis['maps'])} 个\n")
                if analysis['maps']:
                    f.write(f"  - {', '.join(analysis['maps'][:10])}")
                    if len(analysis['maps']) > 10:
                        f.write(f" ... 等 {len(analysis['maps'])} 个")
                    f.write("\n")
                
                f.write(f"- **NPC**: {len(analysis['npcs'])} 个\n")
                if analysis['npcs']:
                    f.write(f"  - {', '.join(analysis['npcs'][:10])}")
                    if len(analysis['npcs']) > 10:
                        f.write(f" ... 等 {len(analysis['npcs'])} 个")
                    f.write("\n")
                
                f.write(f"- **宠物**: {len(analysis['pets'])} 个\n")
                if analysis['pets']:
                    f.write(f"  - {', '.join(analysis['pets'][:10])}")
                    if len(analysis['pets']) > 10:
                        f.write(f" ... 等 {len(analysis['pets'])} 个")
                    f.write("\n")
                
                f.write(f"- **坐标**: {len(analysis['coordinates'])} 个\n")
                if analysis['coordinates']:
                    f.write(f"  - {', '.join(analysis['coordinates'][:10])}")
                    if len(analysis['coordinates']) > 10:
                        f.write(f" ... 等 {len(analysis['coordinates'])} 个")
                    f.write("\n")
                
                f.write(f"- **物品**: {len(analysis['items'])} 个\n")
                if analysis['items']:
                    f.write(f"  - {', '.join(analysis['items'][:10])}")
                    if len(analysis['items']) > 10:
                        f.write(f" ... 等 {len(analysis['items'])} 个")
                    f.write("\n")
                
                f.write(f"- **命令**: {len(analysis['commands'])} 个\n")
                if analysis['commands']:
                    f.write(f"  - 示例: {analysis['commands'][0]}\n")
                
                f.write("\n")
            
            f.write("## 总体统计\n\n")
            f.write(f"- **总文件数**: {len(all_analysis)}\n")
            f.write(f"- **总大小**: {total_size} 字节 ({total_size/1024:.1f} KB)\n")
            f.write(f"- **总行数**: {total_lines} 行\n")
            f.write(f"- **平均文件大小**: {total_size