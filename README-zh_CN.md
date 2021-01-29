# buildout-component

Python Buildout component 工具，一个用来协助将 zc.buildout 的设定元件化的工具程式。

## 介绍

Buildout 是个很棒的 Python 开发与部署环境的工具，但需要大量的设定方能运作良好。

我习惯将 Buildout 每个可重复使用的项目，作为元件 (Component)。如果有需要重复使用的元件，只需将其内容复制到新的专案里即可直接使用，但这仍需依赖手动的设定与组态。

为了简化设定的繁杂，我写了 `buildout-component` 这个小玩意，协助我更方便的设置 Buildout 元件化的环境。

## 功能

- 产生 Buildout Component 的档案架构;
- 透过问答的方式，以产生 Buildout 设定档。

## 安装

安装 `buildout-component`:

    $ pip install buildout-component

## 使用

安装完毕后，可执行 `buildout-component` 指令:

- 设定

        $ buildout-component setup

- 显示设定值

        $ buildout-component show-options

- 建立 Component

        $ buildout-component create

