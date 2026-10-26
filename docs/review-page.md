# 阶段成果网页

发布地址由 GitHub Pages 返回，源为 `main` 分支 `/docs`。此页是公开研究样稿，不作为已核实的完整旅游产品。

- 数据：`data/osaka-pilot.json`
- 模板：`web/index.template.html`
- 生成：`python3 scripts/build_site.py`
- 产物：`docs/index.html`

不依赖数据库、构建服务或付费服务器。移动端单列、桌面多列，支持关键词搜索、免费入场/室内/户外筛选、详情展开、官方来源和地图搜索。

图片暂未加入，不使用示意图充当真实景点照片。星级规则在页面统一说明。未读取成功的对象单独说明；过期活动在浏览时隐藏，资料超过31天暂停展示。页面构建日期与事实核查日期分别显示，不因重新生成而刷新核查日期。

这只是成果查看方式，不代表自动研究、定时月更、数据库或销售功能已经完成。公开链接可被转发；`noindex` 仅请求搜索引擎不要索引，不是访问控制。

更新数据并运行生成命令后，提交和推送至发布分支，GitHub Pages 更新同一个地址。当前未配置定时任务，也不自动推送。

本次发布状态：工程已推送至main。创建Pages站点的API返回 `Resource not accessible by integration` (403)，未启用成功。仓库管理员可在Settings → Pages选择Deploy from a branch、main、/docs并保存。GitHub公布站点地址后需再验证公网访问。GitHub中直接打开HTML文件只会显示源码，不是网站。
