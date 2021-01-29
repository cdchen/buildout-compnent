# buildout-component

Python Buildout component 工具，一個用來協助將 zc.buildout 的設定元件化的工具程式。

## 介紹

Buildout 是個很棒的 Python 開發與部署環境的工具，但需要大量的設定方能運作良好。

我習慣將 Buildout 每個可重複使用的項目，作為元件 (Component)。如果有需要重複使用的元件，只需將其內容複製到新的專案裡即可直接使用，但這仍需依賴手動的設定與組態。

為了簡化設定的繁雜，我寫了 `buildout-component` 這個小玩意，協助我更方便的設置 Buildout 元件化的環境。

## 功能

- 產生 Buildout Component 的檔案架構;
- 透過問答的方式，以產生 Buildout 設定檔。

## 安裝

安裝 `buildout-component`:

    $ pip install buildout-component

## 使用

安裝完畢後，可執行 `buildout-component` 指令:

- 設定

        $ buildout-component setup

- 顯示設定值

        $ buildout-component show-options

- 建立 Component

        $ buildout-component create
    
