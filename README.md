# PythonSeleniumDemoForHZQ
Based on a questionnaire, a workflow was built to automatically fill in the questionnaire data.

使用https://github.com/NanmiCoder/MediaCrawler(合法爬取各大平台数据)
参考https://github.com/Zemelee/wjx实现wjx自动填写

因为这个小demo不想使用外部的存储中间键，我就不想做直接获取数据源的任务了，因为会涉及增删，感觉不太优雅
所以现在是使用MediaCrawler(直接参考它的readme，把json数据粘过来)获取数据，放到json/data.json中，然后启动BussinessAttitudeCollectionDemo就可以了
