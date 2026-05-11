# Codex Plugin Unlocker

Codex Plugin Unlocker 是一个面向 Windows 版 Codex Desktop 的最小启动器。启动器通过 Chromium DevTools Protocol 启动 Codex，并注入一段小型渲染进程脚本，使 API Key 模式下的插件界面可用。

本项目是第三方本地工具，不是 OpenAI 官方发布版本。

## 功能

- 解锁 API Key 模式下的 Codex Desktop 插件侧边栏入口。
- 启用因 `App unavailable` / 应用不可用前端检查而禁用的插件安装按钮。
- 保持侧边栏原始名称 `插件` / `Plugins`，不追加额外标记。
- 不包含会话删除、会话移动、Markdown 导出、watcher 自动接管、Codex 数据库写入。
- Codex 已经以普通方式运行且没有调试端口时，启动器直接退出，不杀 Codex 进程。

## 环境要求

- Windows
- Codex Desktop
- Python 3.11+
- Node.js，仅用于安装脚本中的 JavaScript 语法检查

## 快速安装

克隆仓库后运行：

```powershell
.\scripts\install.ps1
```

安装脚本会创建项目本地 `.venv`、安装包依赖、运行测试、检查注入脚本语法，并创建桌面快捷方式：

```text
Codex Plugin Unlocker.lnk
```

## 使用方式

1. 关闭普通方式启动的 Codex Desktop 窗口。
2. 通过 `Codex Plugin Unlocker.lnk` 启动 Codex。
3. 从 Codex 侧边栏进入插件页面。

Codex 已经通过调试端口 `9229` 运行时，启动器会直接注入到该窗口。Codex 已经运行但没有调试端口时，启动器会退出并提示先关闭 Codex。

## 手动命令

```powershell
python -m codex_plugin_unlocker launch
python -m codex_plugin_unlocker install-shortcut
python -m codex_plugin_unlocker uninstall-shortcut
codex-plugin-unlocker launch
```

## 卸载

```powershell
.\scripts\uninstall.ps1
```

卸载脚本会移除桌面快捷方式和 Windows 卸载项。仓库目录与 `.venv` 会保留，便于审查或手动删除。

## 失败日志

启动器失败日志写入：

```text
%USERPROFILE%\.codex-plugin-unlocker\launcher.log
```

## 安全说明

该工具通过 Chromium DevTools Protocol 向本地 Codex Desktop 渲染进程注入 JavaScript。注入脚本只修改前端状态，不修补 Codex 安装文件，不注册 watcher，不添加开机启动项，不修改 `state_5.sqlite`，不删除本地对话数据。

解锁逻辑依赖 Codex Desktop 的前端实现细节。Codex Desktop 更新后，相关页面结构变化可能导致工具失效。

## 开发验证

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[test]"
.\.venv\Scripts\python.exe -m pytest -q
node --check codex_plugin_unlocker/inject/plugin-unlock.js
```
