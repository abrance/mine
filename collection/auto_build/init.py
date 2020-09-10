from configobj import ConfigObj

# config = ConfigObj('./conf.ini')

"""
setting_info:
site_id

"""


class RewriteConf(object):
    def __init__(self, conf_path, setting_info):
        print('\n\nconf_path: {}\n\nsetting_info: {}'.format(conf_path, setting_info))
        self.settings_dc = setting_info
        self.config = ConfigObj(conf_path, encoding='UTF8')
        self.write()

    def write(self):
        self.config.write()
        # self.config[]
        # config['panel']['last_modify_time'] = now
        # config.write()


class CliRewrite(object):
    def __init__(self, conf_path, setting_info):
        self.settings_dc = setting_info
        print('\n\nconf_path: {}\n\nsetting_info: {}'.format(conf_path, setting_info))
        self.config = ConfigObj(conf_path[0], encoding='UTF8')
        self.dconfig = ConfigObj(conf_path[1], encoding='UTF8')
        self.write()
        # super(CliRewrite, self).__init__(conf_path, setting_info)

    def write(self):
        op = self.config['client']
        op['site_id'] = self.settings_dc.get('site_id')
        op['sgw_port'] = self.settings_dc.get('sgw_listen')
        op['mds_port'] = self.settings_dc.get('mds_listen')
        op['asm_ip'] = self.settings_dc.get('cli_asm_ip')
        op['asm_port'] = self.settings_dc.get('cli_asm_port')
        op['monitor_ip'] = self.settings_dc.get('monitor_ip')
        op['monitor_port'] = self.settings_dc.get('monitor_listen_port')

        dop = self.dconfig['client']
        dop['region_id'] = self.settings_dc.get('region_id')
        dop['monitoring_obj_info'] = self.settings_dc.get('monitoring_obj_info')
        self.config.write()
        self.dconfig.write()


class FPTRewrite(RewriteConf):
    def __init__(self, conf_path, setting_info):
        super(FPTRewrite, self).__init__(conf_path, setting_info)

    def write(self):
        super(FPTRewrite, self).write()
        op = self.config['file_portal']
        op['region_id'] = self.settings_dc.get('region_id')
        op['monitor_ip'] = self.settings_dc.get('monitor_ip')
        op['monitor_port'] = self.settings_dc.get('monitor_listen_port')
        op['monitor_username'] = self.settings_dc.get('monitor_username')
        op['monitor_password'] = self.settings_dc.get('monitor_password')
        op['database_ip'] = self.settings_dc.get('redis_ip')
        op['database_password'] = self.settings_dc.get('redis_password')
        op['sgw_dir_port'] = self.settings_dc.get('sgw_http_listen_port')

        op['fpt_asm_ip'] = self.settings_dc.get('asm_ip')
        op['fpt_asm_port'] = self.settings_dc.get('asm_port')
        op['fpt_id'] = self.settings_dc.get('fpt_id')
        op['shared_path'] = self.settings_dc.get('fpt_shared_path')
        super(FPTRewrite, self).write()


class MDSRewrite(RewriteConf):
    def __init__(self, conf_path, setting_info):
        super(MDSRewrite, self).__init__(conf_path, setting_info)

    def write(self):
        super(MDSRewrite, self).write()
        # glo_op = self.config['DEFAULT']
        db_op = self.config['mysql_db1']
        local_op = self.config['local_config']
        asm_op = self.config['asm_config']

        db_op['host'] = self.settings_dc.get('mds_db_ip')
        db_op['db'] = self.settings_dc.get('mds_db')

        local_op['region_id'] = self.settings_dc.get('region_id')
        local_op['announce_listen_port'] = self.settings_dc.get('mds_listen')
        local_op['local_listen_port'] = self.settings_dc.get('mds_listen')

        asm_op['listen_ipv4'] = self.settings_dc.get('mds_asm_ip')
        asm_op['listen_port'] = self.settings_dc.get('mds_asm_port')
        super(MDSRewrite, self).write()


class MonitorRewrite(RewriteConf):
    def __init__(self, conf_path, setting_info):
        super(MonitorRewrite, self).__init__(conf_path, setting_info)

    def write(self):
        op = self.config['monitor']

        op['server_ip'] = self.settings_dc.get('monitor_ip')
        op['server_port'] = self.settings_dc.get('monitor_listen_port')
        super(MonitorRewrite, self).write()


class SDMRewrite(RewriteConf):
    def __init__(self, conf_path, setting_info):
        super(SDMRewrite, self).__init__(conf_path, setting_info)

    def write(self):
        super(SDMRewrite, self).write()
        fpt_db_op = self.config['mysql_db']
        file_port_op = self.config['file_port']
        sdm_op = self.config['sdm_settings']
        mds_op = self.config['mds']

        fpt_db_op['host'] = self.settings_dc.get('fpt_db_ip')
        fpt_db_op['db'] = self.settings_dc.get('fpt_db')

        file_port_op['url'] = 'https://{}:{}/api/exclude/keylist'.\
            format(self.settings_dc.get('fpt_asm_ip'), self.settings_dc.get('fpt_asm_port'))

        sdm_op['scan_path'] = self.settings_dc.get('sdm_scan_path')
        sdm_op['shared_path'] = self.settings_dc.get('sdm_shared_path')

        mds_op['host'] = self.settings_dc.get('mds_db_ip')
        mds_op['db'] = self.settings_dc.get('mds_db')
        super(SDMRewrite, self).write()


class ASMRewrite(object):
    """
    需要 配置asm信息
    conf_path:
    module_name: mds| cli| fpt| sgw
    # role: mds|……
    role_id:
    ip:
    port:
    rest_port:
    """
    def __init__(self, asm_module_info):
        self.settings_dc = asm_module_info
        self.module_name = None
        self.conf_path = None
        self.config = None
        # self.role = None
        self.role_id = None
        self.ip = None
        self.port = None
        self.rest_port = None
        self.monitor_ip = None
        self.monitor_listen_port = None

        self.fill()
        self.write()
        print('write asm success')

    def fill(self):
        self.module_name = self.settings_dc.get('module_name')
        self.conf_path = self.settings_dc.get('conf_path')
        self.config = ConfigObj(self.conf_path, encoding='UTF8')
        # self.role = self.settings_dc.get('role')
        self.role_id = self.settings_dc.get('role_id')
        self.ip = self.settings_dc.get('ip')
        self.port = self.settings_dc.get('port')
        self.rest_port = self.settings_dc.get('rest_port')
        self.monitor_ip = self.settings_dc.get('monitor_ip')
        self.monitor_listen_port = self.settings_dc.get('monitor_listen_port')

    def write(self):
        ser_op = self.config['service_control']
        status_op = self.config['status_center']
        rest_op = self.config['restful_config']
        listen_op = self.config['listening']

        ser_op['current_role'] = self.module_name
        ser_op['current_id'] = self.role_id

        status_op['host'] = self.monitor_ip

        rest_op['restful_host'] = self.monitor_ip
        rest_op['restful_port'] = self.monitor_listen_port

        listen_op['listen_ip'] = self.ip
        listen_op['listen_port'] = self.port
        listen_op['listen_rest_port'] = self.rest_port
        self.config.write()


class SettingsLoader(object):
    pass
