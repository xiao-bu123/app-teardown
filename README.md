# app-teardown

> 把一个 App / Windows 客户端，按「逐页截图 → 页面层级树 → 功能清单 → 可交付文档」跑成一条可复用流程。

一套给 AI Agent 用的调研 skill：装到机器上、逐页点开、拍下来、写成人能看的报告。适用于 Android App、Windows 桌面客户端、内嵌 H5 的产品。

## 它做什么

- **逐页下钻**：一级 Tab → 二级页 → 弹窗层 → 支付/H5，每页一张真实截图。
- **静态取证**：安装体积、签名主体、内核驱动、路由表、缓存、WebView2、网络端口。
- **外部核对**：官网版本、定价、备案主体、口碑、竞品价格，标注来源可信度。
- **一份数据，五份产出**：内容写进一个 JSON，一条命令生成桌面 HTML / 手机 HTML / Markdown / 单文件 Markdown / 飞书版。

## 产出

| 文件 | 说明 |
|---|---|
| `report.html` | 桌面版单文件：侧栏导航 + 可视结构图 + 页面卡片 + 表格 |
| `report_mobile.html` | 手机版单文件：单列自适应，体积约为桌面版一半 |
| `report.md` | Markdown，图片引用 `shots/` |
| `report_single.md` | 单文件 Markdown，图片 base64 内嵌，可直接转发 |
| `feishu_doc.md` | 飞书文档版，`@./shots/` 路径 |

## 安装

```bash
git clone <this-repo> ~/.dsh/skills/app-teardown
# Windows: C:\Users\<you>\.dsh\skills\app-teardown
```

## 使用

在 Agent 输入框里输入 `/` 选择 `app-teardown`，或者直接说人话：

```
调研一下这个客户端：E:\apps\XX
按上次的格式，给 XX 做一份页面树 + 功能清单
```

## 前置条件

- 能运行目标的机器：Windows 本机 / Android 真机 + adb / 模拟器
- 目标已安装并尽量已登录
- Windows 客户端常以管理员运行，脚本需要能提权
- Python 3 + Pillow（生成 HTML / MD）

## 目录

```
SKILL.md            入口：流程、包内地图、硬规则
references/         平台操作、取证、写作、格式、踩坑
scripts/            截图 / 点击 / 提权 / adb / 报告生成 / 自检
templates/          报告骨架与 JSON 模板
examples/           真实项目数据（外星仔加速器 PC 版，17 页）
```

## 边界

不支付、不发短信验证码、不点注销、不开准星等危险功能；加速类用完立即停，退出客户端并复原系统状态。

## License

MIT
