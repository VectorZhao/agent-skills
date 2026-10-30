# Agent Skills

可复用的 AI Skills 集合。每个 Skill 单独放在 `skills/<skill-name>/`，可按需复制到支持 Agent Skills 的运行环境；本仓库不会自动连接设备、安装软件或发起打印。

## 当前收录

| Skill | 用途 |
| --- | --- |
| [fdm-structural-dfam](skills/fdm-structural-dfam/SKILL.md) | 在 FDM/FFF 功能件建模阶段考虑载荷路径、局部失效、层间剥离、连接、打印方向、材料与验证。通用核心适用于 X2D，另有按需读取的机型核对说明。 |
| [read-wechat-articles](skills/read-wechat-articles/SKILL.md) | 读取微信公众号公开文章并提取正文和文章信息，供摘要、核验或评论使用。 |

## 使用

将完整的 `skills/<skill-name>/` 目录交给支持 `SKILL.md` 的 AI，或按对应应用文档放入它的 Skill 发现目录。Skill 可能依赖随附的脚本、参考文件或模板。

示例请求：

> 使用 fdm-structural-dfam 设计一个设备支架。先建立载荷和边界条件，比较至少两种打印朝向，再生成参数化 CAD，并列明几何检查、切片检查和实际载荷测试的状态。

## 可选网格检查

```bash
python3 -m pip install -r skills/fdm-structural-dfam/requirements.txt
python3 skills/fdm-structural-dfam/scripts/mesh_audit.py part.stl --units mm --json part.audit.json
python3 -m unittest discover -s skills/fdm-structural-dfam/tests -v
```

此脚本只检查部分网格几何条件。它不计算应力，不验证真实壁厚、打印路径、材料性能或承载能力。

## read-wechat-articles 测试

该 Skill 的测试只依赖 Python 标准库：

```bash
python3 -m unittest discover -s skills/read-wechat-articles/tests -v
```

## 新增 Skill

见 [CONTRIBUTING.md](CONTRIBUTING.md)。许可证尚未指定；发布前由仓库所有者决定是否添加开源许可证。
