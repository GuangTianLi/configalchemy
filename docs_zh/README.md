# ConfigAlchemy

ConfigAlchemy是受到Kubernetes声明式资源的启发，使用声明式配置的方式来构建和交付应用程序的配置框架。
通过声明式的方式，结合环境变量，配置文件等静态有优先级覆盖的设计，可以让应用程序在不同环境的交付变得容易，
并且可以让应用程序的配置更加灵活，维护更加的简单。
而作为框架和包的设计者来说，可以更好更加有序得能让用户方便统一得使用配置以达到不同的效果。

# 实践

通常来说，对于一个从简单到复杂的应用程序，配置是一个非常重要的部分，而通常越复杂的应用程序的配置项就越多，
而且结合了其使用的框架的配置项的情况下，配置的更改就变得格外的不方便，并且不好控制。

所以根据生产环境的实践经验来看，模块化配置是非常重要的一环，以下将以一个简单的例子来说明：

> 所有配置项皆需要全大写。

## 静态配置

这是一个最初版本的应用程序，它只声明了一份项目默认使用的配置，并且没有启用ConfigAlchemy特性，即是一份静态的配置。
而且对于默认配置`DefaultConfig`而言，我们希望它代表了这个项目所有能更改的所有配置项，
并且根据Python的语法声明了其名称，类型，以及默认值（而该默认值在大多数开发环境应下应该开箱即用），甚至通过注释来详细描述该配置项的含义。

```python
from configalchemy import BaseConfig

class DefaultConfig(BaseConfig):
    # 数据库连接地址
    DB_URL = "mysql://localhost:6379"
# 显式实例化该配置，并且在整个项目中使用import的方式来显式使用
config = DefaultConfig()
```

## 配置文件动态配置

而通常在应用程序实际的交付过程中，静态配置中所配置的默认值不能满足其他环境的需求，
这个时候通常的做法是使用声明式配置文件来进行动态配置。

```python
from configalchemy import BaseConfig

class DefaultConfig(BaseConfig):
    # 显式声明所启用的配置文件
    CONFIGALCHEMY_CONFIG_FILE = "config.json"
    # 数据库连接地址
    DB_URL = "mysql://localhost:6379"
# 显式实例化该配置，并且在整个项目中使用import的方式来显式使用
config = DefaultConfig()
```

`config.json`:

```json
{
    "DB_URL": "mysql://prod.mysql:6379"
}
```

通过显式声明配置文件的方式可以让配置文件中的配置覆盖原先的默认值，从而达到交付不同环境时使用不同的配置，
即此时`config.DB_URL`的值为`mysql://prod.mysql:6379`。

## 环境变量

通过使用配置文件的方式的确可以满足交付不同的环境，但是当配置文件被声明时，其文件理应存在，
这样就不满足默认值足以开箱即用的原则，并且在实际生产环境过程中，配置文件存在复用的可能，
所以需要更高优先级的方式来进行工作负载级别的配置。因此**环境变量**的特性就为此进行服务。

```python
from configalchemy import BaseConfig

class DefaultConfig(BaseConfig):
    # 显式启用环境变量，并且捕捉以TEST_开头所有环境变量，进行覆盖。(特定前缀，避免环境变量冲突)
    CONFIGALCHEMY_ENV_PREFIX = "TEST_"
    # 显式声明所启用的配置文件，默认为空，即默认不需要配置文件
    CONFIGALCHEMY_CONFIG_FILE = ""
    # 数据库连接地址
    DB_URL = "mysql://localhost:6379"
    # 工作进程数
    WORKER_COUNT = 4
# 显式实例化该配置，并且在整个项目中使用import的方式来显式使用
config = DefaultConfig()
```

利用环境变量覆盖的特性，我们只需要在交付过程中，设置环境变量`TEST_CONFIGALCHEMY_CONFIG_FILE`为`config.json`即可。
而如果需要修改特定工作负载的工作进程数，即设置环境变量`TEST_WORKER_COUNT`即可。

## 模块化

随着项目规模的发展，配置项会越来越多，如果堆积在一个类下面，会让管理和维护变得困难，所以推荐使用模块化的方式，模块化配置。

```python
from configalchemy import BaseConfig

class APIServerDefaultConfig(BaseConfig):
    # 数据库连接地址
    DB_URL = "mysql://localhost:6379"
    # 工作进程数
    WORKER_COUNT = 4

class DefaultConfig(BaseConfig):
    # 显式启用环境变量，并且捕捉以TEST_开头所有环境变量，进行覆盖。(特定前缀，避免环境变量冲突)
    CONFIGALCHEMY_ENV_PREFIX = "TEST_"
    # 显式声明所启用的配置文件，默认为空，即默认不需要配置文件
    CONFIGALCHEMY_CONFIG_FILE = ""

    API_SERVER_CONFIG = APIServerDefaultConfig()

# 显式实例化该配置，并且在整个项目中使用import的方式来显式使用
config = DefaultConfig()
api_server_config = config.API_SERVER_CONFIG
```

模块化配置之后可以统一的通过单一配置文件的方式进行动态配置，也可以通过环境变量覆盖子模块的方式进行精细化控制。

根模块配置文件：
```json
{
    "API_SERVER_CONFIG": {
        "DB_URL": "mysql://prod.mysql:6379"
    }
}
```
环境变量即可使用`Dot Notation`语法进行修改，如`TEST_API_SERVER_CONFIG.WORKER_COUNT`。
