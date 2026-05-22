# MEMORY.md - 项目长期记忆

## 项目索引

### 1. Daily Booking Dashboard（NEW - 2026-05-22）
- **描述**：基于 Master Data-Bob/daily booking.xlsx 的数据仪表板
- **生成器**：`generate_daily_booking_dashboard.py`
- **输出**：`daily_booking_dashboard.html`（自包含 HTML，26.3MB）
- **数据源**：SFTP `Master Data-Bob/daily booking.xlsx`（54,042行）
- **功能**：Multi-VVD搜索多选、CUL Code搜索多选、POL/DEL搜索多选过滤、KPI卡片（20ft/40ft/TEU/Booking数/Container Weight）、Summary透视表（TRUNK LANE→CUL CODE→POR Region/DEL）、TEU by POL & DEL图表、Volume by DEL (Weight)图表、可搜索数据表、Custom Notes面板（localStorage）
- **本地预览**：`http://localhost:8765/daily_booking_dashboard.html`

### 2. 其他数据文件（本地 data/ 目录）
- `AVG Contribution By Vessel.xlsx`：1,652行，平均贡献率 (Master Data - Elaine)
- `REX Rate.xlsx`：~40行，REX 运价 (Master Data - Elaine)
- `Income Data Base-Marketing.xlsx`：59,255行，完整收入数据 (Master Data - Elaine)

### 3. SFTP 连接信息
- 服务器：10.5.4.2:6622，用户 finebiuser
- Master Data - Elaine/：AVG Contribution, REX Rate, Income Data Base
- Master Data-Bob/：daily booking.xlsx, Daily Schedule/（日报文件）

## 项目规范
- 所有仪表板功能写入生成器源码（Python），禁止直接编辑 HTML
- 数据嵌入为 JSON → 单文件自包含 HTML → 浏览器直接使用
- 遵循小步增量修改原则，备份优先
