# 后端 API 文档
## 基础 URL  

http://<服务器IP>:5000

---

## 1. 设置车位状态 

- URL  
  `POST /set_parklot`  
- 请求体  
  ```json
  {
    "mac": "MAC地址", 
    "val" : 0 or 1
  }

  //成功响应(201)
  //错误相应(400 , 404)
  ```

