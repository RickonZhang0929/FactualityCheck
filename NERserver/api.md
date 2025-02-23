


# NER API 接口文档

## 1. 接口概述

该接口接收一个文本字符串（sentence），执行命名实体识别（NER）任务，并返回固定的实体及其类型。

## 2. 接口路径

```
POST /ner
```

## 3. 请求示例

### 请求方式

```
POST /ner
```

### 请求头

```
Content-Type: application/json
```

### 请求体

```json
{
  "sentence": "Apple is looking at buying U.K. startup for $1 billion"
}
```

### 参数说明

| 参数      | 类型   | 描述                       | 是否必填 |
|-----------|--------|----------------------------|----------|
| sentence | string | 要进行NER分析的句子文本   | 是       |

## 4. 响应示例

### 成功响应

```json
{
  "entities": [
    {"text": "Apple", "label": "ORG"},
    {"text": "U.K.", "label": "GPE"},
    {"text": "$1 billion", "label": "MONEY"}
  ]
}
```

### 错误响应

```json
{
  "error": "Sentence is required"
}
```

## 5. 错误码

| 错误码 | 描述                                     |
|--------|------------------------------------------|
| 400    | 请求缺少 `sentence` 字段                |
| 500    | 服务器内部错误，处理请求时发生异常     |

## 6. 使用注意事项

- 请确保在请求中提供有效的 `sentence` 字段。
- 确保Flask服务器已经启动并运行在 `http://127.0.0.1:5000`。
```