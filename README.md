# PytestAutoApi - 自动化API测试框架

## 📖 项目简介

PytestAutoApi是一个基于Python和pytest的自动化API测试框架，支持YAML格式的测试用例定义、数据驱动测试、业务流程测试等多种测试模式。

## ✨ 核心特性

### 🎯 多种测试用例模式
- **单接口测试**：单个API接口的独立测试
- **数据驱动测试**：使用parametrize实现多组数据测试
- **流程用例测试**：单文件中多个接口按顺序执行
- **业务流程测试**：跨文件组合多个用例形成完整业务流程

### 🔧 丰富的断言功能
- **等于断言**：验证响应内容等于预期值
- **包含断言**：验证响应内容包含预期值
- **不包含断言**：验证响应内容不包含特定值
- **数据库断言**：支持数据库查询结果验证

### 🚀 高级功能
- **失败重试**：支持配置重试次数和指数退避策略
- **延迟执行**：支持测试用例执行前的延迟等待
- **用例跳过**：支持条件性跳过测试用例
- **敏感信息过滤**：自动过滤密码、token等敏感信息

### 📊 完善的报告系统
- **Allure报告**：生成美观的测试报告
- **详细日志**：断言失败时显示完整请求和响应信息
- **步骤追踪**：业务流程测试按步骤展示执行情况

## 🏗️ 项目结构

```
PytestAutoApi/
├── configs/                 # 配置文件目录
│   ├── setting.py          # 基础配置
│   ├── test.yaml           # 测试环境配置
│   └── uat.yaml            # UAT环境配置
├── testcases/              # 测试用例目录
│   └── AccountingCenter/   # 业务模块
│       └── client/         # 客户端接口
│           ├── login.yaml                 # 登录接口
│           └── AccountManagement/         # 账户管理模块
│               └── account_list_query.yaml # 账户列表查询
├── utils/                  # 工具类目录
│   ├── file_tools/         # 文件操作工具
│   ├── helper_tools/       # 核心工具类
│   ├── mysql_tools/        # 数据库工具
│   └── requests_tools/     # 请求处理工具
└── extract.yaml           # 变量提取文件
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 安装依赖
pip install -r requirements.txt

# 安装Allure报告工具
# Windows: scoop install allure
# Mac: brew install allure
```

### 2. 配置环境

编辑 `configs/setting.py` 文件：

```python
# 执行用例的环境
ENV = "test"

# 公共参数
global_header = {
    "Content-type": "application/json",
}
```

### 3. 编写测试用例

#### 单接口用例示例

```yaml
- feature: 账务中心
  story: 登录
  title: 登录成功
  request:
    method: post
    url: ${get_env()}gateway/admin/user/login
    json: { "appId": "sys_admin", "userName": "test", "password": "***" }
  extract:
    token: [ json, "$.data.token", 0 ]
  validate:
    equals:
      断言状态码为200: [ "200", "respCode" ]
    contains:
      断言响应包含token: [ "token", "text" ]
```

#### 数据驱动用例示例

```yaml
- feature: 账务中心-账户管理
  story: 账户列表查询
  title: '$ddt{title}'
  request:
    method: post
    url: ${get_env()}gateway/std-account-client/std/account/page
    json: { "belongBrand": '$ddt{belongBrand}', "pageNum": 1, "pageSize": 10 }
  validate:
    equals:
      断言状态为true: [ "True", "success" ]
  parametrize:
    - [ title, belongBrand ]
    - [ "根据品牌查询", "LSHM" ]
    - [ "查询所有数据", "" ]
```

#### 业务流程用例示例

```yaml
scene_name: 账户完整业务流程
desc: 登录 → 查询账户 → 禁用账户
cases:
  - case: login.yaml
    desc: 用户登录获取token
  - case: account_list_query.yaml
    desc: 查询账户列表并提取账户信息
config:
  continue_on_failure: false
  timeout: 300
  retry_count: 1
```

### 4. 执行测试

```bash
# 执行所有测试用例
pytest testcases/test_all_case.py -vs

# 执行特定测试用例
pytest testcases/test_all_case.py::TestAllCase::test_login -vs

# 生成Allure报告
pytest testcases/test_all_case.py --alluredir=./report/allure_raw
allure serve ./report/allure_raw
```

## 🔧 核心组件说明

### 1. 通用工具类 (CommonUtils)

提供项目中常用的重复代码逻辑封装：

```python
from utils.helper_tools.common_utils import CommonUtils

# 获取项目根目录
root_dir = CommonUtils.get_project_root()

# 读取YAML文件
data = CommonUtils.read_yaml_file("config.yaml")

# 过滤敏感信息
filtered_headers = CommonUtils.filter_sensitive_data(headers, "headers")
```

### 2. 断言控制器 (AssertControl)

支持多种断言类型，断言失败时显示完整请求和响应信息：

```python
from utils.helper_tools.assert_control import AssertControl

# 执行断言
assert_control = AssertControl()
assert_control.assert_all_case(
    resp=response,
    assert_type="equals",
    assert_rules={"断言状态码": ["200", "status_code"]},
    request_info=request_params
)
```

### 3. 业务流程控制器 (BusinessFlowControl)

支持跨文件的业务流程测试：

```python
from utils.helper_tools.business_flow_control import BusinessFlowControl

# 判断是否为业务流程用例
if BusinessFlowControl.is_business_flow(yaml_path):
    # 读取业务流程用例
    case_list = BusinessFlowControl.read_business_flow(yaml_path)
```

### 4. 用例控制器 (CaseControl)

用例执行入口，支持重试、延迟、跳过等功能：

```python
from utils.requests_tools.case_control import use_case_execution

# 执行单个用例
use_case_execution(case_info)
```

## 📋 断言类型说明

| 断言类型 | 说明 | 示例 |
|---------|------|------|
| equals | 等于断言 | `[ "200", "status_code" ]` |
| contains | 包含断言 | `[ "token", "text" ]` |
| not_contains | 不包含断言 | `[ "error", "text" ]` |
| db_equals | 数据库等于断言 | `[ "SELECT name FROM users", "user_name" ]` |
| db_contains | 数据库包含断言 | `[ "SELECT email FROM users", "text" ]` |
| db_not_contains | 数据库不包含断言 | `[ "SELECT status FROM orders", "text" ]` |

## 🔄 变量替换系统

### 环境变量替换
```yaml
url: ${get_env()}gateway/admin/user/login
```

### 提取变量替换
```yaml
headers: { "Authorization": "Bearer ${read_extract(token)}" }
```

### 数据驱动变量替换
```yaml
json: { "belongBrand": "$ddt{belongBrand}" }
```

## 🛠️ 配置说明

### 环境配置

在 `configs/test.yaml` 中配置测试环境：

```yaml
env:
  base_url: "https://acc-test.hnlshm.com/"
  job_url: "https://acc-jobtest.hnlshm.com/"
```

### 数据库配置

在 `configs/test.yaml` 中配置数据库连接：

```yaml
mysql:
  db_user: "mmhm_dev_user"
  db_password: "your_password"
  db_host: "pc-bp15ra9oiu192nc9e-pub.rwlb.rds.aliyuncs.com"
  db_database: "mmhm_stdacc"
  db_port: 3306
```

## 📈 测试报告

### Allure报告特性
- **美观的界面**：现代化的测试报告界面
- **步骤追踪**：业务流程测试按步骤展示
- **失败分析**：详细的断言失败信息
- **环境信息**：测试环境配置信息

### 日志输出
断言失败时显示完整信息：
```
断言失败：断言响应内容包含特定字符串
接口请求信息:
  headers: {'Content-type': 'application/json'}
  json: {'appId': 'sys_admin', 'password': '***FILTERED***'}
  method: post
  url: https://acc-test.hnlshm.com/gateway/admin/user/login
预期值表达式: text
原始预期值: '特定字符串'
实际获取值: '{"respCode":"200","data":{"token":"..."}}'
```

## 🔍 调试技巧

### 1. 查看变量提取
```python
from utils.helper_tools.helper_control import HelperControl

token = HelperControl.read_extract('token')
print(f"当前token: {token}")
```

### 2. 调试请求参数
```python
from utils.helper_tools.extract_control import ExtractControl

request_params = ExtractControl().change(case_info.request)
print(f"请求参数: {request_params}")
```

### 3. 查看测试用例结构
```python
from utils.helper_tools.ddt_control import read_testcase

case_list = read_testcase("testcases/login.yaml")
print(f"用例结构: {case_list}")
```

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进这个项目！

### 开发规范
- 遵循PEP 8代码规范
- 为所有方法添加详细的注释
- 使用通用工具类避免代码重复
- 保持向后兼容性

## 📄 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者！

---

**PytestAutoApi** - 让API测试更简单、更高效！