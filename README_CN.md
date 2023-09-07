# chat2db-sqlcoder-deploy部署

语言：中文  | [English](README.md)

## 📖 简介
这个工程介绍了如何在阿里云上免费部署sqlcoder的8bit量化模型，并将大模型应用到Chat2DB客户端中。

！！！请注意，sqlcoder项目主要是针对SQL生成的，所以在自然语言转SQL方面表现较好，但是在SQL解释、SQL优化和SQL转化方面表现略差，仅供大家实验参考，切勿迁怒于模型或产品。

## 📦 硬件要求
|      模型       | 最低GPU显存(推理) | 最低GPU显存(高效参数微调) |
|:-------------:|:-----------:|:---------------:|
| sqlcoder-int8 |    20GB     |      20GB       |


## 📦 部署
### 📦 在阿里云DSW中部署8bit模型

1. [阿里云免费使用平台](https://free.aliyun.com/)申请DSW免费试用。
<img src="https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/4j6OJdYA60Y7n3p8/img/e5141c12-0279-451b-9e47-5125a5a34731.png?x-oss-process=image/resize,w_1280,m_lfit,limit_1">
2. 创建一个DSW实例，资源组选择可以抵扣资源包的资源组，实例镜像选择pytorch:1.12-gpu-py39-cu113-ubuntu20.04
<img src="https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/4j6OJdYA60Y7n3p8/img/d5ed7234-afb3-49de-a2a2-db6aa0424efa.png?x-oss-process=image/resize,w_1280,m_lfit,limit_1">
<img src="https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/4j6OJdYA60Y7n3p8/img/26c3961f-967d-4b11-8a81-4b037c833344.png?x-oss-process=image/resize,w_1280,m_lfit,limit_1">
3. 安装本仓库中的[requirements.txt](requirements.txt)中的依赖包

```bash
pip install -r requirements.txt
```

4. 因为要跑8bit的量化模型，所以还需要下载bitsandbytes包，执行下面的命令下载最新版本，否则cuda有可能会出现不兼容的情况

```bash
pip install -i https://test.pypi.org/simple/ bitsandbytes
```

5. 在DSW实例中打开一个terminal，在目录/mnt/workspace下创建sqlcoder-model和sqlcoder文件夹
6. 在sqlcoder-model文件夹下下载sqlcoder模型，执行下面的命令，请确保模型里面的几个bin文件下载完整且正确

```bash
git clone https://huggingface.co/defog/sqlcoder
```

7. 将本项目下的api.py和prompt.md文件拷贝到sqlcoder文件夹下
8. 安装fastapi相关包

```bash
pip install fastapi nest-asyncio pyngrok uvicorn
```

9. 在sqlcoder文件夹下执行下面的命令，启动api服务

```bash
python api.py
```

10. 执行以上步骤之后，你将得到一个api url，类似于`https://dfb1-34-87-2-137.ngrok.io`。
<img src="https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/4j6OJdYA60Y7n3p8/img/086b2121-19d3-4bff-a188-91e51d0c208d.png?x-oss-process=image/resize,w_1280,m_lfit,limit_1">

11. 将api url复制到chat2db客户端中，即可开始使用模型生成SQL了。参考下图进行配置
<img src="https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/4j6OJdYA60Y7n3p8/img/ca844185-2744-49e0-ab75-245e19b872d6.png?x-oss-process=image/resize,w_640,m_lfit,limit_1">

- 实验结果如下
<img src="https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/4j6OJdYA60Y7n3p8/img/d3f319f6-2612-4352-ab46-99ff92dace63.png?x-oss-process=image/resize,w_1280,m_lfit,limit_1">
* 注意: 模型推理时间可能会比较长，会有明显的卡顿。

### 📦 在阿里云DSW中部署非量化模型
* 如果机器资源允许，可以尝试部署非量化的sqlcoder模型，在生成SQL的准确率上会比8bit的模型高一些，但是需要更多的显存和更长的推理时间。
* 部署非量化模型的步骤同上，只需要将api.py文件中的模型加载改成float16的模型即可，具体如下：

```python
model = AutoModelForCausalLM.from_pretrained("/mnt/workspace/sqlcoder-model/sqlcoder",
                                      trust_remote_code=True,
                                      torch_dtype=torch.float16,
                                      # load_in_8bit=True,
                                      device_map="auto",
                                      use_cache=True)
```

### 📦 在其他云资源上部署sqlcoder模型
* 本教程虽然写的是在阿里云DSW环境上完成的，但是本教程中的脚本和命令并没有进行任何定制，理论上遵循以上步骤，可以在任何云资源上进行部署。