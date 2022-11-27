import yaml
import os
import sys
import requests
import logging
import re

def log_sys():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    try:
        os.remove(f'{sys.path[0]}/run_log.log')
    except:
        None
    file_handler = logging.FileHandler(f'{sys.path[0]}/run_log.log',mode='w')
    file_handler.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger

def get_dic(path):
    d = {}
    f = open(path,'r',encoding='utf-8')
    try:
        d = yaml.load(f,Loader=yaml.FullLoader)
    except:
        logger.warning("Fail to load the file!")
        return None
    f.close()
    return d

def config_download(url):
    logger.info("Obtain information from subscription.")
    try:
        with open(f'{sys.path[0]}/original.yaml','wb') as f:
            my_file = requests.get(url,timeout=50000)
            f.write(my_file.content)
            logger.info("Subscription file is saved to original.yaml.")
            f.close()
    except:
        logger.warning("Fail to obtain information from URL!")
        return None
    yaml_path = os.path.join(sys.path[0],'original.yaml')
    yaml_dic = get_dic(yaml_path)
    return yaml_dic

def proxy_groups_type(config): # change proxy type to url_test
    logger.info("Start to modify the setting in proxy-groups.")
    try:
        for groups in config['proxy-groups']:
            if groups['name'] == 'Video':
                groups['type'] = 'url-test'
                logger.info(f"Change {groups['name']} type to {groups['type']}.")
                groups['url'] = 'http://www.gstatic.cn/generate_204'
                groups['tolerance'] = 50
                logger.info(f"Set {groups['name']} tolerance as {groups['tolerance']}.")
                remove_proxy_list = ['Express']
                for index_name in remove_proxy_list:
                    try:
                        index_loc = groups['proxies'].index(index_name)
                        del groups['proxies'][index_loc]
                        logger.info(f"Remove {index_name} from {groups['name']}.")
                    except:
                        logger.info(f"Did not find {index_name} in {groups['name']} ")
            elif groups['name'] == 'NETFLIX':
                groups['type'] = 'fallback'
                logger.info(f"Change {groups['name']} type to {groups['type']}.")
                groups['url'] = 'http://www.gstatic.cn/generate_204'
                groups['tolerance'] = 50
                logger.info(f"Set {groups['name']} tolerance as {groups['tolerance']}.")
                remove_proxy_list = ['Auto-Edge','DIRECT']
                for index_name in remove_proxy_list:
                    try:
                        index_loc = groups['proxies'].index(index_name)
                        del groups['proxies'][index_loc]
                        logger.info(f"Remove {index_name} from {groups['name']}.")
                    except:
                        logger.info(f"Did not find {index_name} in {groups['name']} ")
        logger.info("Modification in proxy-groups finish.")
        return config
    except:
        logger.warning("Cannot find proxy-groups in original.yaml!")
        return None

def proxies_fix(config): # fix the bug in path
    logger.info("Start to fix the setting in proxies.[Debug Process]")
    try:
        for proxy in config['proxies']:
            if proxy['type'] == 'trojan':
                path = proxy['ws-opts']['path']
                yaml.add_implicit_resolver(None, re.compile(path))
            elif proxy['type'] == 'ss':
                try:
                    path = proxy['plugin-opts']['path']
                    yaml.add_implicit_resolver(None, re.compile(path))
                except:
                    None
            elif proxy['type'] == 'vmess':
                path = proxy['ws-path']
                yaml.add_implicit_resolver(None, re.compile(path))
        logger.info("Finish to fix the setting in proxies.[Debug Process]")
        return config
    except:
        logger.warning("Did not fix the bug in proxies (headers) in original.yaml!")
        return None

def config_modify(config):
    try:
        logger.info("Start to modify the file.")
        config['allow-lan'] = True # allow access from lan
        logger.info("Set allow-lan = true.")
        config['external-controller'] = '0.0.0.0:9090'
        logger.info("Set external-controller = 0.0.0.0:9090")
        config = proxy_groups_type(config)
        config = proxies_fix(config)
        logger.info("Modification Success!")
        return config
    except:
        logger.warning("Did not find settings!")

def main(url):
    try:
        original_dic = config_download(url)
        try:
            modify_dic = config_modify(original_dic)
            with open(f'{sys.path[0]}/config.yaml','w') as f:
                _ = yaml.dump(modify_dic,f,sort_keys=False,default_flow_style=False,encoding='utf-8',allow_unicode=True)
                logger.info("Modified file is saved to config.yaml.")
        except:
            logger.warning("Modification Fail! PLEASE CHECK original.yaml!")
    except:
        logger.warning("Fail to download file from subscription link!")

url = 'http://'
logger = log_sys()
main(url)
