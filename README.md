# Skills List

[English](./README.en.md)

自用 Skills 合集，包含一些奇妙的 skills，仅供娱乐。

## Quickstart

预览仓库内可安装的 skills：

```bash
npx skills add squarezhong/skills-list --list
```

安装仓库内全部 skills：

```bash
npx skills add squarezhong/skills-list --all
```

只安装某一个 skill：

```bash
npx skills add squarezhong/skills-list --skill adjust-retail-sales-by-index
```

## 仓库结构

```text
skills/
  finance/
    adjust-retail-sales-by-index/
  system/
    analyze-macos-system-data/
  tools/
    summarize-bilibili-video/
```

## Skills

### Finance

#### `adjust-retail-sales-by-index`

*生成按特定消费指数口径修正后的社零数据。*

示例用法：

```text
请使用 adjust-retail-sales-by-index：基于我提供的上证消费50成分股对国家统计局2019-2026年1-6月社会消费品零售总额数据进行修正和汇总。
```

### System

#### `analyze-macos-system-data`

*用只读方式分析 macOS Storage 里的 System Data 占用，识别大体量目录的来源、风险等级和谨慎清理候选项。*

示例用法：

```text
请使用 analyze-macos-system-data 分析 macOS System Data 为什么占用这么大，列出最大的确认来源和安全后续步骤。
```

### Tools

#### `summarize-bilibili-video`

*抓取 Bilibili 视频字幕并基于字幕内容进行总结。*

示例用法：

```text
请使用 summarize-bilibili-video 总结这个视频：https://www.bilibili.com/video/BV1EfTe6jEVe
```

## 添加新 Skill

新增 skill 时沿用当前结构：

```text
skills/<category>/<skill-name>/*
```

## License

MIT
