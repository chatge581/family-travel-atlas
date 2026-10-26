# Family Travel Atlas

大阪及周边亲子地点研究样稿。当前包含10个研究对象、9张候选卡；不是已完成的旅游产品。

**[查看全部地点卡 →](output/osaka-pilot.md)**

这个入口在手机和电脑浏览器中均可阅读。地点数据、研究记录与网页工程保存在本仓库。

## 图文网页

适配手机和电脑的静态网页已放在 `docs/index.html`，支持地点搜索、免费入场/室内/户外筛选和详情展开。GitHub文件页不执行HTML；需要开启GitHub Pages。

[打开 Pages 设置](https://github.com/chatge581/family-travel-atlas/settings/pages)，设置：

1. **Source** 选择 **Deploy from a branch**。
2. **Branch** 选择 **main**，目录选择 **/docs**，点击 **Save**。
3. 等待GitHub部署完成，使用设置页显示的 **Visit site** 链接。

当前集成调用启用Pages接口返回403，尚未确认网页已发布。不要把源代码地址当成已经上线的网页地址。

## 数据与更新

- [结构化数据](data/osaka-pilot.json)
- [本轮研究与边界](docs/osaka-pilot.md)
- [成果页维护方式](docs/review-page.md)

```sh
python3 scripts/build_site.py
python3 -m unittest discover -s scripts -p 'test_*.py' -v
```

网页从已核实的记录生成，不自动刷新事实核查日期。当前未配置定时研究、自动月更或销售服务。
