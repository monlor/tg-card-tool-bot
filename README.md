# 卡粉工具箱 (Card Tool Bot)

这是一个基于Python和python-telegram-bot库开发的Telegram机器人,用于提供汇率查询和卡Bin查询等功能。该机器人支持查询最近指定天数内的汇率变化情况,并自动删除一段时间后的查询结果消息。

## 特性

### 汇率查询

- 使用 /rate 命令查询最近指定天数内的汇率变化情况
- 支持自定义主货币、汇率查询天数、消息删除延迟等参数  
- 基于环境变量配置,方便部署和维护

### 卡BIN查询

- 使用 /bin 命令查询银行卡Bin信息,包括发卡行和卡种类型

## 部署方式

```
docker run -d -e BOT_TOKEN=xxx ghcr.io/monlor/tg-card-tool-bot:main
```

## 使用方式

1. 在 Telegram 客户端中搜索并与机器人 @card_tool_bot 对话
2. 输入 `/rate [货币代码] [金额]` 查询汇率,例如 `/rate CNY 100`
3. 输入 `/bin [卡号前6位或8位]` 查询卡Bin信息,例如 `/bin 456783`

## 配置选项

以下配置参数可在 .env 文件中修改:

- `BOT_TOKEN`: 机器人令牌
- `MAIN_CURRENCY`: 主货币,默认为美元 CNY
- `DELETE_DELAY`: 消息自动删除延迟,单位为秒
- `QUERY_DAYS`: 查询最近天数,默认为 5 天

## 开发者

该项目由 TGScriptMaster 开发,如需任何支持或定制需求,请联系我们。

欢迎Star并Fork该项目,也可提出建议或反馈。让我们一起为"卡粉工具箱"机器人的发展贡献力量!