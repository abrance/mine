# 档案二期部署配置
    conf.ini:
    global 为全局配置
    build_path 是部署位置，如果存在同名的文件夹会将之前的改名
    
    填上off说明不从svn 上拉代码，不然都会去拉
    svn代码地址，拉代码必填
    pro_dir_name 如果svn为off，那么必填这个项目地址：项目顶层目录
    
    web_app 如果是网页应用需要填，如 fpt，monitor
    web_app_url 如果web_app 不为空，就必填
    
    global 全局配置详细
    
