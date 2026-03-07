# 🚀 快速启动指南

## 环境设置完成 ✅

已创建 conda 环境 `aia-work` 并安装所有依赖。

## 测试结果

✅ 所有核心模块测试通过：
- 数据库初始化成功（3个默认意图：HR、Legal、Finance）
- 向量存储功能正常
- 模块导入无错误

## 下一步操作

### 1. 配置 API 密钥

```bash
cd backend
cp .env.example .env
```

编辑 `.env` 文件，添加你的 Qwen API 密钥：
```
QWEN_API_KEY=your_actual_api_key_here
```

获取 API 密钥：https://dashscope.aliyun.com/

### 2. 启动后端服务

```bash
conda activate aia-work
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

访问：http://localhost:8000 查看 API 状态

### 3. 启动管理后台（新终端）

```bash
conda activate aia-work
cd dashboard
export BACKEND_URL=http://localhost:8000
streamlit run app.py
```

访问：http://localhost:8501 使用管理界面

## 功能测试

### 上传文档
1. 打开管理后台 → Knowledge Base
2. 上传 PDF 或 DOCX 文件
3. 选择关联的意图类别

### 配置 Bot
1. Frontend Integration 页面
2. 配置 Telegram 或 Slack 凭证
3. 设置 webhook URL

### 查询测试
使用 API 直接测试：
```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the vacation policy?", "source": "api"}'
```

## 项目结构

```
intelliknow-kms/
├── backend/          # FastAPI 后端
│   ├── app/
│   │   ├── api/      # API 端点
│   │   ├── services/ # 核心服务
│   │   └── main.py   # 应用入口
│   └── data/         # 数据存储
├── dashboard/        # Streamlit 管理界面
└── docs/            # 文档
```

## 故障排查

**问题：数据库文件未找到**
- 确保 `backend/data/` 目录存在
- 运行测试脚本会自动创建

**问题：FAISS 索引错误**
- 检查向量维度是否匹配（默认 1536）
- 删除 `data/faiss_index/` 重新初始化

**问题：API 连接失败**
- 确认 Qwen API 密钥正确
- 检查网络连接

## 开发建议

1. 先配置 API 密钥并测试 LLM 连接
2. 上传示例文档测试文档处理
3. 使用 API 测试查询功能
4. 最后配置 Telegram/Slack 集成

祝开发顺利！🎉
