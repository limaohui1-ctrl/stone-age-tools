#!/usr/bin/env python3
"""
石器时代坐标管理系统
用于管理、验证和优化石器时代脚本中的坐标
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import re

class CoordinateManager:
    def __init__(self):
        self.data_dir = "/root/.openclaw/workspace/石器时代坐标数据"
        self.create_data_dir()
        
        # 坐标数据库文件
        self.coordinates_file = os.path.join(self.data_dir, "coordinates.json")
        self.validation_rules_file = os.path.join(self.data_dir, "validation_rules.json")
        
        # 加载或初始化数据
        self.coordinates = self.load_coordinates()
        self.validation_rules = self.load_validation_rules()
        
        # 从已分析的脚本中提取的坐标示例
        self.example_coordinates = [
            {"name": "渔村医院", "x": 89, "y": 51, "map": "渔村", "script": "自动跑环脚本_带错误反馈.asc"},
            {"name": "村长家", "x": 67, "y": 53, "map": "渔村", "script": "NG25练2DMM脚本.asc"},
            {"name": "宠物店", "x": 72, "y": 48, "map": "渔村", "script": "NG25无敌2DMM培养.asc"},
            {"name": "武器店", "x": 58, "y": 62, "map": "渔村", "script": "NG25精细逻辑跑环.asc"},
            {"name": "道具店", "x": 63, "y": 57, "map": "渔村", "script": "妖攻MM.asc"},
        ]
        
    def create_data_dir(self):
        """创建数据目录"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            print(f"创建数据目录: {self.data_dir}")
    
    def load_coordinates(self) -> Dict:
        """加载坐标数据"""
        if os.path.exists(self.coordinates_file):
            try:
                with open(self.coordinates_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {"coordinates": [], "last_updated": None}
        else:
            return {"coordinates": [], "last_updated": None}
    
    def load_validation_rules(self) -> Dict:
        """加载验证规则"""
        default_rules = {
            "map_bounds": {
                "渔村": {"min_x": 0, "max_x": 100, "min_y": 0, "max_y": 100},
                "加加村": {"min_x": 0, "max_x": 120, "min_y": 0, "max_y": 120},
                "萨姆吉尔": {"min_x": 0, "max_x": 150, "min_y": 0, "max_y": 150},
            },
            "coordinate_patterns": [
                {"pattern": r"walkpos\s+(\d+)\s*,\s*(\d+)", "type": "walkpos"},
                {"pattern": r"waitpos\s+(\d+)\s*,\s*(\d+)", "type": "waitpos"},
                {"pattern": r"(\d+)\s*,\s*(\d+)", "type": "general"},
            ],
            "validation_levels": {
                "strict": {"max_deviation": 5, "require_map": True},
                "normal": {"max_deviation": 10, "require_map": False},
                "lenient": {"max_deviation": 20, "require_map": False},
            }
        }
        
        if os.path.exists(self.validation_rules_file):
            try:
                with open(self.validation_rules_file, 'r', encoding='utf-8') as f:
                    loaded_rules = json.load(f)
                    # 合并默认规则和加载的规则
                    for key in default_rules:
                        if key not in loaded_rules:
                            loaded_rules[key] = default_rules[key]
                    return loaded_rules
            except:
                return default_rules
        else:
            return default_rules
    
    def save_coordinates(self):
        """保存坐标数据"""
        self.coordinates["last_updated"] = datetime.now().isoformat()
        with open(self.coordinates_file, 'w', encoding='utf-8') as f:
            json.dump(self.coordinates, f, ensure_ascii=False, indent=2)
    
    def save_validation_rules(self):
        """保存验证规则"""
        with open(self.validation_rules_file, 'w', encoding='utf-8') as f:
            json.dump(self.validation_rules, f, ensure_ascii=False, indent=2)
    
    def extract_coordinates_from_text(self, text: str) -> List[Dict]:
        """从文本中提取坐标"""
        coordinates = []
        
        for rule in self.validation_rules["coordinate_patterns"]:
            pattern = rule["pattern"]
            matches = re.finditer(pattern, text)
            
            for match in matches:
                x = int(match.group(1))
                y = int(match.group(2))
                
                coordinate = {
                    "x": x,
                    "y": y,
                    "type": rule["type"],
                    "context": text[max(0, match.start()-50):min(len(text), match.end()+50)],
                    "line_number": text[:match.start()].count('\n') + 1,
                }
                
                coordinates.append(coordinate)
        
        return coordinates
    
    def validate_coordinate(self, coordinate: Dict, map_name: str = None, level: str = "normal") -> Dict:
        """验证坐标的有效性"""
        x = coordinate["x"]
        y = coordinate["y"]
        
        validation_result = {
            "coordinate": coordinate,
            "is_valid": True,
            "warnings": [],
            "errors": [],
            "suggestions": [],
        }
        
        # 检查坐标范围
        if map_name and map_name in self.validation_rules["map_bounds"]:
            bounds = self.validation_rules["map_bounds"][map_name]
            
            if x < bounds["min_x"] or x > bounds["max_x"]:
                validation_result["is_valid"] = False
                validation_result["errors"].append(f"X坐标 {x} 超出地图 {map_name} 范围 ({bounds['min_x']}-{bounds['max_x']})")
            
            if y < bounds["min_y"] or y > bounds["max_y"]:
                validation_result["is_valid"] = False
                validation_result["errors"].append(f"Y坐标 {y} 超出地图 {map_name} 范围 ({bounds['min_y']}-{bounds['max_y']})")
        
        # 检查是否为常见坐标
        similar_coords = self.find_similar_coordinates(x, y, map_name)
        if similar_coords:
            validation_result["suggestions"].append(f"找到 {len(similar_coords)} 个相似坐标")
            for similar in similar_coords[:3]:  # 显示前3个
                validation_result["suggestions"].append(f"  相似: {similar['name']} ({similar['x']},{similar['y']}) - {similar.get('script', '未知脚本')}")
        
        # 检查坐标是否为常见值
        common_coords = self.get_common_coordinates()
        for common in common_coords:
            if abs(x - common["x"]) <= 5 and abs(y - common["y"]) <= 5:
                validation_result["warnings"].append(f"坐标接近常见位置: {common['name']} ({common['x']},{common['y']})")
        
        return validation_result
    
    def find_similar_coordinates(self, x: int, y: int, map_name: str = None, max_distance: int = 10) -> List[Dict]:
        """查找相似坐标"""
        similar = []
        
        # 检查示例坐标
        for coord in self.example_coordinates:
            if abs(x - coord["x"]) <= max_distance and abs(y - coord["y"]) <= max_distance:
                if not map_name or coord["map"] == map_name:
                    similar.append(coord)
        
        # 检查已保存的坐标
        for coord in self.coordinates.get("coordinates", []):
            if abs(x - coord["x"]) <= max_distance and abs(y - coord["y"]) <= max_distance:
                if not map_name or coord.get("map") == map_name:
                    similar.append(coord)
        
        return similar
    
    def get_common_coordinates(self) -> List[Dict]:
        """获取常见坐标"""
        return self.example_coordinates
    
    def add_coordinate(self, name: str, x: int, y: int, map_name: str, script: str = None, notes: str = None):
        """添加新坐标"""
        new_coord = {
            "name": name,
            "x": x,
            "y": y,
            "map": map_name,
            "script": script,
            "notes": notes,
            "added_date": datetime.now().isoformat(),
            "usage_count": 0,
        }
        
        # 验证坐标
        validation = self.validate_coordinate(new_coord, map_name)
        
        if validation["is_valid"]:
            self.coordinates.setdefault("coordinates", []).append(new_coord)
            self.save_coordinates()
            print(f"✅ 坐标已添加: {name} ({x},{y}) - {map_name}")
            
            if validation["warnings"]:
                print("  警告:")
                for warning in validation["warnings"]:
                    print(f"    • {warning}")
            
            if validation["suggestions"]:
                print("  建议:")
                for suggestion in validation["suggestions"]:
                    print(f"    • {suggestion}")
        else:
            print(f"❌ 坐标验证失败: {name} ({x},{y})")
            for error in validation["errors"]:
                print(f"    • {error}")
            
            print("是否仍然添加? (y/n): ", end="")
            response = input().strip().lower()
            if response == 'y':
                self.coordinates.setdefault("coordinates", []).append(new_coord)
                self.save_coordinates()
                print(f"⚠️ 坐标已添加（带有错误）: {name} ({x},{y})")
    
    def analyze_script_file(self, filepath: str):
        """分析脚本文件中的坐标"""
        if not os.path.exists(filepath):
            print(f"❌ 文件不存在: {filepath}")
            return
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            filename = os.path.basename(filepath)
            print(f"分析脚本文件: {filename}")
            print("=" * 60)
            
            # 提取坐标
            coordinates = self.extract_coordinates_from_text(content)
            
            if not coordinates:
                print("未找到坐标")
                return
            
            print(f"找到 {len(coordinates)} 个坐标:")
            print()
            
            valid_count = 0
            warning_count = 0
            
            for i, coord in enumerate(coordinates, 1):
                print(f"{i}. 坐标: ({coord['x']},{coord['y']})")
                print(f"   类型: {coord['type']}")
                print(f"   行号: {coord['line_number']}")
                
                # 验证坐标
                validation = self.validate_coordinate(coord)
                
                if validation["is_valid"]:
                    valid_count += 1
                    print(f"   状态: ✅ 有效")
                else:
                    print(f"   状态: ❌ 无效")
                
                if validation["warnings"]:
                    warning_count += len(validation["warnings"])
                    print(f"   警告: {', '.join(validation['warnings'])}")
                
                if validation["suggestions"]:
                    print(f"   建议: {validation['suggestions'][0]}")
                
                print(f"   上下文: {coord['context']}")
                print()
            
            print("=" * 60)
            print(f"分析完成:")
            print(f"  • 总坐标数: {len(coordinates)}")
            print(f"  • 有效坐标: {valid_count}")
            print(f"  • 警告数量: {warning_count}")
            print(f"  • 建议添加: {len(coordinates) - valid_count}")
            
            # 询问是否保存坐标
            if coordinates:
                print("\n是否保存这些坐标到数据库? (y/n): ", end="")
                response = input().strip().lower()
                if response == 'y':
                    for coord in coordinates:
                        self.add_coordinate(
                            name=f"脚本坐标_{coord['line_number']}",
                            x=coord['x'],
                            y=coord['y'],
                            map_name="未知",
                            script=filename,
                            notes=f"从 {filename} 第 {coord['line_number']} 行提取"
                        )
        
        except Exception as e:
            print(f"分析文件时出错: {e}")
    
    def generate_coordinate_report(self):
        """生成坐标报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = os.path.join(self.data_dir, f"coordinate_report_{timestamp}.md")
        
        coordinates = self.coordinates.get("coordinates", [])
        example_coords = self.example_coordinates
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# 石器时代坐标管理报告\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**总坐标数**: {len(coordinates) + len(example_coords)}\n\n")
            
            f.write("## 📊 坐标统计\n\n")
            f.write(f"- **数据库坐标**: {len(coordinates)} 个\n")
            f.write(f"- **示例坐标**: {len(example_coords)} 个\n")
            f.write(f"- **最后更新**: {self.coordinates.get('last_updated', '从未更新')}\n\n")
            
            f.write("## 📋 坐标列表\n\n")
            
            if coordinates:
                f.write("### 数据库坐标\n\n")
                f.write("| 名称 | 坐标 | 地图 | 脚本 | 添加时间 |\n")
                f.write("|------|------|------|------|----------|\n")
                
                for coord in coordinates:
                    f.write(f"| {coord['name']} | ({coord['x']},{coord['y']}) | {coord.get('map', '未知')} | {coord.get('script', '未知')} | {coord.get('added_date', '未知')[:10]} |\n")
                
                f.write("\n")
            
            f.write("### 示例坐标\n\n")
            f.write("| 名称 | 坐标 | 地图 | 脚本 |\n")
            f.write("|------|------|------|------|\n")
            
            for coord in example_coords:
                f.write(f"| {coord['name']} | ({coord['x']},{coord['y']}) | {coord['map']} | {coord['script']} |\n")
            
            f.write("\n## 🗺️ 地图边界规则\n\n")
            f.write("| 地图 | X范围 | Y范围 |\n")
            f.write("|------|-------|-------|\n")
            
            for map_name, bounds in self.validation_rules["map_bounds"].items():
                f.write(f"| {map_name} | {bounds['min_x']}-{bounds['max_x']} | {bounds['min_y']}-{bounds['max_y']} |\n")
            
            f.write("\n## 🔧 使用建议\n\n")
            f.write("1. **坐标验证**: 在脚本中使用坐标前进行验证\n")
            f.write("2. **坐标管理**: 定期更新和维护坐标数据库\n")
            f.write("3. **错误处理**: 对无效坐标提供清晰的错误信息\n")
            f.write("4. **优化建议**: 根据相似坐标优化路径规划\n")
        
        print(f"坐标报告已生成: {report_file}")
        return report_file
    
    def interactive_mode(self):
        """交互模式"""
        print("=" * 60)
        print("石器时代坐标管理系统")
        print("=" * 60)
        
        while True:
            print("\n请选择操作:")
            print("1. 添加新坐标")
            print("2. 分析脚本文件")
            print("3. 查看坐标列表")
            print("4. 生成坐标报告")
            print("5. 验证坐标")
            print("6. 退出")
            
            choice = input("\n请输入选项 (1-6): ").strip()
            
            if choice == "1":
                print("\n--- 添加新坐标 ---")
                name = input("坐标名称: ").strip()
                x = input("X坐标: ").strip()
                y = input("Y坐标: ").strip()
                map_name = input("地图名称: ").strip()
                script = input("脚本名称 (可选): ").strip() or None
                notes = input("备注 (可选): ").strip() or None
                
                try:
                    self.add_coordinate(name, int(x), int(y), map_name, script, notes)
                except ValueError:
                    print("❌ 坐标必须是数字")
            
            elif choice == "2":
                print("\n--- 分析脚本文件 ---")
                filepath = input("脚本文件路径: ").strip()
                self.analyze_script_file(filepath)
            
            elif choice == "3":
                print("\n--- 坐标列表 ---")
                coordinates = self.coordinates.get("coordinates", [])
                example_coords = self.example_coordinates
                
                print(f"数据库坐标 ({len(coordinates)} 个):")
                for i, coord in enumerate(coordinates, 1):
                    print(f"  {i}. {coord['name']}: ({coord['x']},{coord['y']}) - {coord.get('map', '未知')}")
                
                print(f"\n示例坐标 ({len(example_coords)} 个):")
                for i, coord in enumerate(example_coords, 1):
                    print(f"  {i}. {coord['name']}: ({coord['x']},{coord['y']}) - {coord['map']}")
            
            elif choice == "4":
                print("\n--- 生成坐标报告 ---")
                report_file = self.generate_coordinate_report()
                print(f"报告已生成: {report_file}")
            
            elif choice == "5":
                print("\n--- 验证坐标 ---")
                x = input("X坐标: ").strip()
                y = input("Y坐标: ").strip()
                map_name = input("地图名称 (可选): ").strip() or None
                
                try:
                    coord = {"x": int(x), "y": int(y)}
                    validation = self.validate_coordinate(coord, map_name)
                    
                    print(f"\n验证结果:")
                    print(f"  坐标: ({x},{y})")
                    print(f"  地图: {map_name or '未指定'}")
                    print(f"  有效: {'✅ 是' if validation['is_valid'] else '❌ 否'}")
                    
                    if validation['warnings']:
                        print(f"  警告:")
                        for warning in validation['warnings']:
                            print(f"    • {warning}")
                    
                    if validation['errors']:
                        print(f"  错误:")
                        for error in validation['errors']:
                            print(f"    • {error}")
                    
                    if validation['suggestions']:
                        print(f"  建议:")
                        for suggestion in validation['suggestions']:
                            print(f"    • {suggestion}")
                
                except ValueError:
                    print("❌ 坐标必须是数字")
            
            elif choice == "6":
                print("\n退出系统")
                break
            
            else:
                print("❌ 无效选项")

def main():
    """主函数"""
    manager = CoordinateManager()
    
    print("石器时代坐标管理系统 v1.0")
    print("=" * 60)
    
    # 显示系统状态
    coordinates_count = len(manager.coordinates.get("coordinates", []))
    example_count = len(manager.example_coordinates)
    
    print(f"系统状态:")
    print(f"  • 数据库坐标: {coordinates_count} 个")
    print(f"  • 示例坐标: {example_count} 个")
    print(f"  • 地图规则: {len(manager.validation_rules['map_bounds'])} 个")
    print(f"  • 数据目录: {manager.data_dir}")
    
    # 进入交互模式
    manager.interactive_mode()

if __name__ == "__main__":
    main()
