# FDM Structural DfAM

功能性 FDM/FFF 零件的结构设计 Skill。主文件为 `SKILL.md`，按需加载 `references/`，使用 `templates/` 记录工况和审核结果。

结构核心与机型无关，X2D 仅增加设备与双材料检查，不改变力学判断。此包不包含远程设备控制、打印提交或自动安装功能。

网格检查：

```bash
python3 -m pip install -r requirements.txt
python3 scripts/mesh_audit.py part.stl --units mm --json audit.json
python3 -m unittest discover -s tests -v
```

状态 `geometry_screened` 仅表示所实现的几何检查未发现问题，不是机械强度通过。`structural_validation` 始终为 `not_performed`。
