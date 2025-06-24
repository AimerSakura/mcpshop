

------

# MCP商城（SmartStore）API文档

## 认证说明

- 除注册、登录外，所有接口都需要携带 `Authorization: Bearer <access_token>`。
- 认证方式为 OAuth2 password（JWT）。
- HTTP状态码规范：200 成功，204 无内容，400 参数错误，401 未认证，403 无权限，404 未找到，422 校验错误。

------

## 1. 用户与认证

### 1.1 用户注册

- **接口**：`POST /api/auth/register`

- **请求体**（application/json）：

  ```json
  {
    "username": "string(3-50)",     // 必填，用户名，长度3~50
    "email": "user@example.com",    // 必填，Email格式
    "password": "string(≥6)"        // 必填，密码，长度≥6
  }
  ```

- **响应体**（application/json）：

  ```json
  {
    "user_id": 1,                           // int，用户ID
    "username": "zhangsan",                 // string
    "email": "zhangsan@example.com",        // string，邮箱
    "is_admin": false,                      // bool，是否管理员
    "created_at": "2025-06-15T08:00:00Z",   // string, datetime
    "updated_at": null                      // string/datetime/null
  }
  ```

- **参数校验失败示例**（422）：

  ```json
  {
    "detail": [
      {
        "loc": ["body", "username"],
        "msg": "字段长度需至少3",
        "type": "value_error"
      }
    ]
  }
  ```

------

### 1.2 用户登录

- **接口**：`POST /api/auth/token`

- **请求体**（`application/x-www-form-urlencoded`）：

  ```
  username=zhangsan&password=123456
  ```

- **响应体**：

  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer"
  }
  ```

- **参数校验失败示例**（422）：

  ```json
  {
    "detail": [
      {
        "loc": ["body", "username"],
        "msg": "field required",
        "type": "value_error.missing"
      }
    ]
  }
  ```

------

## 2. 商品模块

### 2.1 获取商品列表

- **接口**：`GET /api/products`

- **参数**（Query）：

  - `q`（string，可选，搜索关键词，默认空字符串）
  - `limit`（integer，可选，最小1，最大100，默认20）

- **响应体**（application/json，数组，每个元素如下）：

  ```json
  [
    {
      "sku": "COKE001",                    // string，商品SKU
      "name": "可口可乐",                   // string，商品名称
      "price_cents": 350,                  // int，价格（单位分）
      "stock": 100,                        // int，库存
      "description": "冰镇可乐",           // string/null，商品描述
      "image_url": "http://xx.jpg",        // string/null，图片URL
      "category_id": 1,                    // int/null，分类ID
      "created_at": "2025-06-15T09:00:00Z",// string, datetime
      "updated_at": "2025-06-15T10:00:00Z" // string, datetime
    }
  ]
  ```

------

### 2.2 获取商品详情

- **接口**：`GET /api/products/{sku}`

- **路径参数**：

  - `sku`（string，商品SKU，必填）

- **响应体**（application/json）：

  ```json
  {
    "sku": "COKE001",
    "name": "可口可乐",
    "price_cents": 350,
    "stock": 100,
    "description": "冰镇可乐",
    "image_url": "http://xx.jpg",
    "category_id": 1,
    "created_at": "2025-06-15T09:00:00Z",
    "updated_at": "2025-06-15T10:00:00Z"
  }
  ```

------

### 2.3 新增商品（管理员）

- **接口**：`POST /api/products`

- **权限**：需要管理员Token

- **请求体**（application/json）：

  ```json
  {
    "sku": "SPRITE001",                   // string(≤32), 必填
    "name": "雪碧",                        // string(≤100), 必填
    "price_cents": 320,                   // int, 必填，非负
    "stock": 100,                         // int, 必填，非负
    "description": "清爽雪碧",             // string/null, 必填
    "image_url": "http://xx.jpg",         // string/null, 必填
    "category_id": 1                      // int/null, 必填
  }
  ```

- **响应体**：

  ```json
  {
    "sku": "SPRITE001",
    "name": "雪碧",
    "price_cents": 320,
    "stock": 100,
    "description": "清爽雪碧",
    "image_url": "http://xx.jpg",
    "category_id": 1,
    "created_at": "2025-06-15T10:00:00Z",
    "updated_at": "2025-06-15T10:00:00Z"
  }
  ```

------

### 2.4 修改商品（管理员）

- **接口**：`PATCH /api/products/{sku}`

- **权限**：需要管理员Token

- **路径参数**：

  - `sku`（string，商品SKU，必填）

- **请求体**（application/json，可填任意字段，字段不填则不修改）：

  ```json
  {
    "name": "新商品名",                  // string/null
    "price_cents": 400,                 // int/null
    "stock": 80,                        // int/null
    "description": "新描述",             // string/null
    "image_url": "http://new.jpg",      // string/null
    "category_id": 2                    // int/null
  }
  ```

- **响应体**：

  ```json
  {
    "sku": "SPRITE001",
    "name": "新商品名",
    "price_cents": 400,
    "stock": 80,
    "description": "新描述",
    "image_url": "http://new.jpg",
    "category_id": 2,
    "created_at": "2025-06-15T10:00:00Z",
    "updated_at": "2025-06-15T11:00:00Z"
  }
  ```

------

### 2.5 删除商品（管理员）

- **接口**：`DELETE /api/products/{sku}`
- **权限**：需要管理员Token
- **路径参数**：
  - `sku`（string，商品SKU，必填）
- **响应**：204 无内容

------

## 3. 购物车模块

### 3.1 查看购物车

- **接口**：`GET /api/cart/`

- **响应体**（application/json，数组，每个元素如下）：

  ```json
  [
    {
      "sku": "COKE001",                    // string
      "quantity": 2,                       // int ≥1
      "cart_item_id": 123,                 // int
      "added_at": "2025-06-15T11:00:00Z",  // string, datetime
      "product": {
        "sku": "COKE001",
        "name": "可口可乐",
        "price_cents": 350,
        "stock": 100,
        "description": "冰镇可乐",
        "image_url": "http://xx.jpg",
        "category_id": 1,
        "created_at": "2025-06-15T09:00:00Z",
        "updated_at": "2025-06-15T10:00:00Z"
      }
    }
  ]
  ```

------

### 3.2 添加商品到购物车

- **接口**：`POST /api/cart/`

- **请求体**（application/json）：

  ```json
  {
    "sku": "COKE001",           // string, 必填
    "quantity": 2               // int ≥1, 必填
  }
  ```

- **响应体**（application/json）：

  ```json
  {
    "sku": "COKE001",
    "quantity": 2,
    "cart_item_id": 123,
    "added_at": "2025-06-15T11:00:00Z",
    "product": {
      "sku": "COKE001",
      "name": "可口可乐",
      "price_cents": 350,
      "stock": 100,
      "description": "冰镇可乐",
      "image_url": "http://xx.jpg",
      "category_id": 1,
      "created_at": "2025-06-15T09:00:00Z",
      "updated_at": "2025-06-15T10:00:00Z"
    }
  }
  ```

------

### 3.3 删除购物车项

- **接口**：`DELETE /api/cart/{cart_item_id}`
- **路径参数**：
  - `cart_item_id`（int，必填）
- **响应**：204 无内容

------

### 3.4 清空购物车

- **接口**：`DELETE /api/cart/clear`
- **响应**：204 无内容

------

## 4. 订单模块

### 4.1 下单

- **接口**：`POST /api/orders/`

- **请求体**：无

- **响应体**（application/json）：

  ```json
  {
    "order_id": 1001,                    // int，订单ID
    "total_cents": 700,                  // int，总金额（分）
    "status": "PENDING",                 // string，订单状态
    "created_at": "2025-06-15T11:05:00Z",// string, datetime
    "items": [
      {
        "sku": "COKE001",                // string，商品SKU
        "quantity": 2,                   // int
        "unit_price": 350                // int，单价（分）
      }
    ]
  }
  ```

------

### 4.2 查询自己订单

- **接口**：`GET /api/orders/`
- **响应体**（application/json，数组，每个元素结构同上）

------

### 4.3 管理员查所有订单

- **接口**：`GET /api/orders/all`
- **权限**：需要管理员Token
- **响应体**（application/json，数组，每个元素结构同上）

------

## 5. 用户管理（管理员）

### 5.1 查询所有用户

- **接口**：`GET /api/users/`

- **权限**：需要管理员Token

- **响应体**（application/json，数组，每个元素如下）：

  ```json
  [
    {
      "user_id": 1,                           // int
      "username": "admin",                    // string
      "email": "admin@example.com",           // string
      "is_admin": true,                       // bool
      "created_at": "2025-06-15T08:00:00Z",   // string, datetime
      "updated_at": null                      // string/datetime/null
    }
  ]
  ```

------

### 5.2 删除用户

- **接口**：`DELETE /api/users/{username}`
- **权限**：需要管理员Token
- **路径参数**：
  - `username`（string，必填）
- **响应**：204 无内容

------

## 6. AI助手/智能对话

### 6.1 REST对话接口

- **接口**：`POST /api/chat`

- **请求体**（application/json）：

  ```json
  {
    "text": "帮我把可乐加到购物车"        // string，必填
  }
  ```

- **响应体**（application/json）：

  ```json
  {
    "reply": "已为您添加可乐到购物车",   // string
    "actions": [ ... ]                  // array，具体结构由AI助手逻辑决定
  }
  ```

------

### 6.2 WebSocket对话接口

- **接口**：`ws://<host>/api/chat`
- **发送/接收数据**结构同上，支持多轮对话。

------

## 7. 数据结构（Schema）

### UserOut

```json
{
  "user_id": 1,
  "username": "zhangsan",
  "email": "zhangsan@example.com",
  "is_admin": false,
  "created_at": "2025-06-15T08:00:00Z",
  "updated_at": null
}
```

### ProductOut

```json
{
  "sku": "COKE001",
  "name": "可口可乐",
  "price_cents": 350,
  "stock": 100,
  "description": "冰镇可乐",
  "image_url": "http://xx.jpg",
  "category_id": 1,
  "created_at": "2025-06-15T09:00:00Z",
  "updated_at": "2025-06-15T10:00:00Z"
}
```

### OrderOut

```json
{
  "order_id": 1001,
  "total_cents": 700,
  "status": "PENDING",
  "created_at": "2025-06-15T11:05:00Z",
  "items": [
    {
      "sku": "COKE001",
      "quantity": 2,
      "unit_price": 350
    }
  ]
}
```

### CartItemOut

```json
{
  "sku": "COKE001",
  "quantity": 2,
  "cart_item_id": 123,
  "added_at": "2025-06-15T11:00:00Z",
  "product": {
    "sku": "COKE001",
    "name": "可口可乐",
    "price_cents": 350,
    "stock": 100,
    "description": "冰镇可乐",
    "image_url": "http://xx.jpg",
    "category_id": 1,
    "created_at": "2025-06-15T09:00:00Z",
    "updated_at": "2025-06-15T10:00:00Z"
  }
}
```

------

## 8. 错误响应格式

### 校验错误（422）

```json
{
  "detail": [
    {
      "loc": ["body", "field"],
      "msg": "字段描述",
      "type": "value_error"
    }
  ]
}
```

### 普通错误（如未认证、权限不足、资源不存在等）

```json
{
  "detail": "错误信息"
}
```

------

