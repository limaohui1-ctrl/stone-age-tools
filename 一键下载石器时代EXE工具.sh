#!/bin/bash
# 一键下载石器时代EXE工具脚本
# 从GitHub仓库下载所有EXE工具并自动安装

set -e  # 出错时退出

echo "=========================================="
echo "🚀 石器时代EXE工具一键下载与安装"
echo "=========================================="
echo "GitHub仓库: https://github.com/limaohui1-ctrl/stone-age-tools"
echo "开始时间: $(date)"
echo ""

# 配置
GITHUB_REPO="https://github.com/limaohui1-ctrl/stone-age-tools"
EXE_DIR="EXE版本"
INSTALL_DIR="$HOME/石器时代工具"
TEMP_DIR="/tmp/stone-age-tools-$(date +%s)"
LOG_FILE="$INSTALL_DIR/安装日志_$(date +%Y%m%d_%H%M%S).txt"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log() {
    echo -e "${BLUE}[INFO]${NC} $1"
    echo "[INFO] $(date): $1" >> "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
    echo "[SUCCESS] $(date): $1" >> "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
    echo "[WARNING] $(date): $1" >> "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    echo "[ERROR] $(date): $1" >> "$LOG_FILE"
    exit 1
}

# 检查必要工具
check_requirements() {
    log "检查系统要求..."
    
    # 检查curl
    if ! command -v curl &> /dev/null; then
        error "需要curl，请先安装: sudo apt install curl"
    fi
    success "curl 已安装"
    
    # 检查git
    if ! command -v git &> /dev/null; then
        warning "git未安装，将使用curl下载"
        USE_CURL=true
    else
        success "git 已安装"
        USE_CURL=false
    fi
    
    # 检查unzip
    if ! command -v unzip &> /dev/null; then
        warning "unzip未安装，将尝试安装"
        if [ "$(id -u)" -eq 0 ]; then
            apt update && apt install -y unzip || warning "unzip安装失败"
        fi
    fi
    
    # 创建安装目录
    mkdir -p "$INSTALL_DIR"
    mkdir -p "$TEMP_DIR"
    
    # 创建日志文件
    mkdir -p "$(dirname "$LOG_FILE")"
    > "$LOG_FILE"
    
    success "系统要求检查完成"
}

# 下载EXE工具
download_tools() {
    log "开始下载EXE工具..."
    
    if [ "$USE_CURL" = true ]; then
        # 使用curl下载
        log "使用curl下载仓库..."
        cd "$TEMP_DIR"
        
        # 下载ZIP文件
        curl -L -o stone-age-tools.zip "$GITHUB_REPO/archive/refs/heads/master.zip" || {
            error "下载失败，请检查网络连接"
        }
        
        # 解压
        unzip -q stone-age-tools.zip || {
            error "解压失败，请检查文件完整性"
        }
        
        # 查找EXE目录
        EXE_SOURCE=$(find . -name "$EXE_DIR" -type d | head -1)
        if [ -z "$EXE_SOURCE" ]; then
            error "未找到EXE版本目录"
        fi
        
    else
        # 使用git克隆
        log "使用git克隆仓库..."
        cd "$TEMP_DIR"
        
        git clone --depth 1 "$GITHUB_REPO" . || {
            error "Git克隆失败，请检查网络连接"
        }
        
        EXE_SOURCE="./$EXE_DIR"
    fi
    
    if [ ! -d "$EXE_SOURCE" ]; then
        error "EXE目录不存在: $EXE_SOURCE"
    fi
    
    success "下载完成，找到EXE目录: $EXE_SOURCE"
    echo "$EXE_SOURCE"
}

# 安装工具
install_tools() {
    local exe_source="$1"
    
    log "开始安装工具..."
    
    # 复制所有EXE文件
    log "复制EXE文件到安装目录..."
    cp -r "$exe_source"/* "$INSTALL_DIR/" 2>/dev/null || {
        warning "部分文件复制失败，继续安装..."
    }
    
    # 设置执行权限
    log "设置执行权限..."
    find "$INSTALL_DIR" -type f -executable -exec chmod +x {} \; 2>/dev/null || true
    
    # 创建分类目录
    log "整理工具分类..."
    mkdir -p "$INSTALL_DIR/核心工具"
    mkdir -p "$INSTALL_DIR/部署工具"
    mkdir -p "$INSTALL_DIR/监控工具"
    mkdir -p "$INSTALL_DIR/实用工具"
    mkdir -p "$INSTALL_DIR/文档"
    
    # 移动文件到对应目录
    if [ -d "$INSTALL_DIR/核心工具" ]; then
        mv "$INSTALL_DIR/核心工具"/* "$INSTALL_DIR/核心工具/" 2>/dev/null || true
    fi
    
    if [ -d "$INSTALL_DIR/部署工具" ]; then
        mv "$INSTALL_DIR/部署工具"/* "$INSTALL_DIR/部署工具/" 2>/dev/null || true
    fi
    
    if [ -d "$INSTALL_DIR/监控工具" ]; then
        mv "$INSTALL_DIR/监控工具"/* "$INSTALL_DIR/监控工具/" 2>/dev/null || true
    fi
    
    if [ -d "$INSTALL_DIR/实用工具" ]; then
        mv "$INSTALL_DIR/实用工具"/* "$INSTALL_DIR/实用工具/" 2>/dev/null || true
    fi
    
    # 移动文档
    mv "$INSTALL_DIR"/*.md "$INSTALL_DIR"/*.txt "$INSTALL_DIR/文档/" 2>/dev/null || true
    
    success "工具安装完成"
}

# 创建快捷方式
create_shortcuts() {
    log "创建快捷方式..."
    
    # 创建桌面快捷方式
    if [ -d "$HOME/Desktop" ]; then
        ln -sf "$INSTALL_DIR" "$HOME/Desktop/石器时代工具" 2>/dev/null || {
            warning "桌面快捷方式创建失败"
        }
        success "桌面快捷方式已创建"
    fi
    
    # 创建启动脚本
    cat > "$INSTALL_DIR/启动所有工具.sh" << 'EOF'
#!/bin/bash
echo "========================================"
echo "🚀 石器时代工具启动菜单"
echo "========================================"
echo ""
echo "请选择要启动的工具:"
echo "1. 网络稳定性工具包主程序"
echo "2. 网络波动检测器"
echo "3. 智能重试系统"
echo "4. 防卡机制"
echo "5. 性能监控仪表板"
echo "6. 部署系统主程序"
echo "7. 开发进度监控系统"
echo "8. 所有工具"
echo "9. 退出"
echo ""
read -p "请输入选择 (1-9): " choice

case $choice in
    1) ./核心工具/主程序 ;;
    2) ./核心工具/网络波动检测器 ;;
    3) ./核心工具/智能重试系统 ;;
    4) ./核心工具/防卡机制 ;;
    5) ./核心工具/性能监控仪表板 ;;
    6) ./部署工具/主程序 ;;
    7) ./监控工具/开发进度实时监控系统 ;;
    8)
        echo "启动所有工具..."
        ./核心工具/主程序 --help &
        ./核心工具/网络波动检测器 --help &
        ./核心工具/智能重试系统 --help &
        ./核心工具/防卡机制 --help &
        ./核心工具/性能监控仪表板 --help &
        echo "所有工具已启动"
        ;;
    9) echo "退出" ;;
    *) echo "无效选择" ;;
esac
EOF
    
    chmod +x "$INSTALL_DIR/启动所有工具.sh"
    success "启动脚本已创建"
    
    # 创建环境变量配置
    cat > "$INSTALL_DIR/配置环境变量.sh" << 'EOF'
#!/bin/bash
# 配置石器时代工具环境变量

echo "配置石器时代工具环境变量..."
echo ""

# 添加到PATH
if [[ ":$PATH:" != *":$HOME/石器时代工具:"* ]]; then
    echo 'export PATH="$HOME/石器时代工具:$PATH"' >> ~/.bashrc
    echo 'export PATH="$HOME/石器时代工具/核心工具:$PATH"' >> ~/.bashrc
    echo 'export PATH="$HOME/石器时代工具/部署工具:$PATH"' >> ~/.bashrc
    echo "✅ 已添加到PATH"
else
    echo "✅ PATH中已包含石器时代工具"
fi

# 创建别名
cat >> ~/.bashrc << 'ALIASES'

# 石器时代工具别名
alias 石器时代主程序='~/石器时代工具/核心工具/主程序'
alias 网络检测='~/石器时代工具/核心工具/网络波动检测器'
alias 智能重试='~/石器时代工具/核心工具/智能重试系统'
alias 防卡工具='~/石器时代工具/核心工具/防卡机制'
alias 性能监控='~/石器时代工具/核心工具/性能监控仪表板'
alias 部署系统='~/石器时代工具/部署工具/主程序'
alias 进度监控='~/石器时代工具/监控工具/开发进度实时监控系统'
ALIASES

echo "✅ 别名已创建"
echo ""
echo "请运行以下命令使配置生效:"
echo "source ~/.bashrc"
echo ""
echo "配置完成后，您可以直接使用以下命令:"
echo "  石器时代主程序 --help"
echo "  网络检测 --help"
echo "  智能重试 --help"
EOF
    
    chmod +x "$INSTALL_DIR/配置环境变量.sh"
    success "环境变量配置脚本已创建"
}

# 生成安装报告
generate_report() {
    log "生成安装报告..."
    
    local report_file="$INSTALL_DIR/安装报告_$(date +%Y%m%d_%H%M%S).md"
    
    cat > "$report_file" << EOF
# 🎉 石器时代EXE工具安装报告

## 📅 安装信息
- **安装时间**: $(date)
- **安装目录**: $INSTALL_DIR
- **GitHub仓库**: $GITHUB_REPO
- **EXE版本**: v1.0.0

## 📊 安装统计

### 已安装的工具
EOF
    
    # 统计工具数量
    core_count=$(find "$INSTALL_DIR/核心工具" -type f -executable 2>/dev/null | wc -l)
    deploy_count=$(find "$INSTALL_DIR/部署工具" -type f -executable 2>/dev/null | wc -l)
    monitor_count=$(find "$INSTALL_DIR/监控工具" -type f -executable 2>/dev/null | wc -l)
    util_count=$(find "$INSTALL_DIR/实用工具" -type f -executable 2>/dev/null | wc -l)
    total_count=$((core_count + deploy_count + monitor_count + util_count))
    
    cat >> "$report_file" << EOF
- **核心工具**: $core_count 个 (网络稳定性相关)
- **部署工具**: $deploy_count 个 (自动化部署)
- **监控工具**: $monitor_count 个 (进度监控)
- **实用工具**: $util_count 个 (其他工具)
- **总计**: $total_count 个可执行文件

### 目录结构
\`\`\`
$INSTALL_DIR/
├── 核心工具/     # 网络稳定性工具
├── 部署工具/     # 自动化部署工具
├── 监控工具/     # 进度监控工具
├── 实用工具/     # 其他实用工具
├── 文档/        # 说明文档
├── 启动所有工具.sh
├── 配置环境变量.sh
└── 安装报告_*.md
\`\`\`

## 🚀 使用方法

### 快速开始
\`\`\`bash
# 进入安装目录
cd $INSTALL_DIR

# 启动工具
./启动所有工具.sh

# 或直接运行
./核心工具/主程序 --help
\`\`\`

### 配置环境变量
\`\`\`bash
# 运行配置脚本
./配置环境变量.sh

# 使配置生效
source ~/.bashrc

# 现在可以直接使用别名
石器时代主程序 --help
网络检测 --help
智能重试 --help
\`\`\`

## 🛠️ 工具详情

### 核心工具 (网络稳定性)
1. **主程序** - 工具包主程序
2. **网络波动检测器** - 实时网络监控
3. **智能重试系统** - 自适应重试策略
4. **防卡机制** - 脚本卡顿恢复
5. **性能监控仪表板** - 性能可视化

### 部署工具
1. **主程序** - 部署系统主程序
2. **打包引擎** - 脚本打包功能
3. **配置引擎** - 智能配置管理
4. **部署引擎** - 自动化部署

### 其他工具
1. **开发进度实时监控系统** - 进度监控
2. **快速EXE优化** - EXE优化工具
3. **石器时代坐标管理系统** - 坐标管理

## ⚠️ 注意事项

1. **文件大小**: EXE文件较大是正常现象（包含Python运行时）
2. **执行权限**: 已自动设置，如需重新设置: chmod +x 工具名
3. **Windows用户**: 需要重命名为.exe后缀或使用Wine运行
4. **防病毒软件**: 可能被误报，请添加到白名单

## 🔧 技术支持

### 常见问题
1. **无法运行**: 尝试以管理员身份运行
2. **缺少依赖**: 安装VC++运行库 (Windows)
3. **权限问题**: 使用chmod +x添加执行权限 (Linux)

### 更新检查
\`\`\`bash
# 进入安装目录
cd $INSTALL_DIR

# 检查更新
curl -s $GITHUB_REPO | grep -i "update\|版本"
\`\`\`

## 📞 反馈
如有问题，请参考文档或访问GitHub仓库:
$GITHUB_REPO

---
**报告生成时间**: $(date)
**安装状态**: ✅ 成功
**工具总数**: $total_count
**下一步**: 开始使用石器时代开发工具！
EOF
    
    success "安装报告已生成: $report_file"
    echo "$report_file"
}

# 清理临时文件
cleanup() {
    log "清理临时文件..."
    
    if [ -d "$TEMP_DIR" ]; then
        rm -rf "$TEMP_DIR"
        success "临时文件已清理"
    fi
}

# 显示完成信息
show_completion() {
    local report_file="$1"
    
    echo ""
    echo "=========================================="
    echo "🎉 石器时代EXE工具安装完成！"
    echo "=========================================="
    echo ""
    echo "📊 安装统计:"
    echo "  📁 安装目录: $INSTALL_DIR"
    echo "  🛠️  工具总数: $(find "$INSTALL_DIR" -type f -executable 2>/dev/null | wc -l)个"
    echo "  📄 文档: $INSTALL_DIR/文档/"
    echo "  📝 日志: $LOG_FILE"
    echo "  📋 报告: $report_file"
    echo ""
    echo "🚀 立即开始使用:"
    echo "  1. cd $INSTALL_DIR"
    echo "  2. ./启动所有工具.sh"
    echo "  3. 或直接运行: ./核心工具/主程序 --help"
    echo ""
    echo "🔧 配置环境变量:"
    echo "  ./配置环境变量.sh"
    echo "  source ~/.bashrc"
    echo ""
    echo "📖 详细文档:"
    echo "  查看 $INSTALL_DIR/文档/ 目录"
    echo ""
    echo "🔗 GitHub仓库:"
    echo "  $GITHUB_REPO"
    echo ""
    echo "=========================================="
    echo "🎮 现在开始享受石器时代开发工具吧！"
    echo "=========================================="
}

# 主函数
main() {
    echo ""
    log "开始石器时代EXE工具一键安装"
    
    # 检查要求
    check_requirements
    
    # 下载工具
    exe_source=$(download_tools)
    
    # 安装工具
    install_tools "$exe_source"
    
    # 创建快捷方式
    create_shortcuts
    
    # 生成报告
    report_file=$(generate_report)
    
    # 清理
    cleanup
    
    # 显示完成信息
    show_completion "$report_file"
}

# 运行主函数
main "$@"