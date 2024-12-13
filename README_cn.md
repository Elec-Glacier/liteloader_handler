[English](https://github.com/Elec-Glacier/liteloader_handler/blob/main/README.md) | **中文**

# Bedrock Liteloader Handler
一个让基岩版也能使用MCDR及其插件的服务端处理器

## 使用之前
原版的BDS是不能输出玩家聊天的。所以你可以使用行为包或者是更改服务端来实现玩家聊天输出

## 使用说明
1. 从仓库[releases](https://github.com/Elec-Glacier/liteloader_handler/releases)中现在最新版本
2. 将下载的文件放入到MCDR的"plugins"文件夹里
3. 启动MCDR
4. 更改config文件夹中的配置文件，选择处理器（默认是原版处理器）
5. 重载配置文件

## MCDR插件安装注意
由于基岩版和Java版判若两个游戏，所以在使用其他插件之前，确保知道其是如何工作的并保证能正常运行。

## 注意事项
由于[BDS-3791](https://bugs.mojang.com/browse/BDS-3791)，你可能需要插件修改服务端进行修复，如[UnicodeFixer](https://www.minebbs.com/resources/unicodefixer.6991/)。
