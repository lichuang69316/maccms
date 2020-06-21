# -*- coding: utf-8 -*-
import platform,os,requests

# 修改php配置文件
php_ini = '''cat << EOF > /tmp/php.sh
if [ -f "/etc/php.ini" ]
then
sed -i "s/^post_max_size/;post_max_size/g" /etc/php.ini
sed -i "s/^max_execution_time/;max_execution_time/g" /etc/php.ini
sed -i "s/^max_input_time/;max_input_time/g" /etc/php.ini
sed -i "s/^date.timezone/;date.timezone/g" /etc/php.ini
echo "post_max_size = 16M" >> /etc/php.ini
echo "max_execution_time = 300" >> /etc/php.ini
echo "max_input_time = 300" >> /etc/php.ini
echo "date.timezone = "Asia/Shanghai"" >> /etc/php.ini
echo "extension=php_mbstring.so" >> /etc/php.ini
fi
EOF'''

# 登录数据库修改密码
mysql_passwd = '''mysqlpass="$(grep 'temporary password' /var/log/mysqld.log | awk '{print $11}')"
mysql --connect-expired-password -uroot -p''$mysqlpass'' -e "alter user 'root'@'localhost' identified by '1qaz@WSX';"'''

# 添加nginx的php配置
nginx_php = '''location ~ .php$ {
    root           /usr/share/nginx/html;
    fastcgi_pass   127.0.0.1:9000;
    fastcgi_index  index.php;
    fastcgi_param  SCRIPT_FILENAME  /usr/share/nginx/html$fastcgi_script_name;
    include        fastcgi_params;
}'''

# 判断操作系统
def type_system():
    # 判断操作系统，并将结果赋值于info
    info = platform.platform()
    # Windows操作系统返回结果为0
    if 'indows' in info:
        return 0
    # Ubuntu操作系统返回结果为1
    elif 'buntu' in info:
        return 1
    # Centos操作系统返回结果为2
    elif 'entos' in info:
        return 2
    # 其他类型操作系统返回结果为3
    else:
        return 3

# 关闭防火墙，关闭内核安全机制
def firewalld():
    os.system('systemctl stop firewalld')
    os.system('setenforce 0')

# 启用可选 rpms 的软件仓库
def install():
    os.system('yum -y install epel-release')
    os.system('yum -y install wget unzip')
    os.system('yum -y update')
    os.system('rpm -Uvh https://mirror.webtatic.com/yum/el7/webtatic-release.rpm')
    os.system('rpm -ivh https://dev.mysql.com/get/mysql57-community-release-el7-11.noarch.rpm')
    os.system('yum -y install yum-utils')
    os.system('yum-config-manager --enable rhel-7-server-optional-rpms')

# 安装nginx
def install_nginx():
    os.system('yum -y install nginx')
    os.system('systemctl enable nginx')
    os.system('systemctl start nginx')

# 安装配置php
def install_php():
    os.system('yum -y php*')
    os.system('yum -y install php70w php70w-gd php70w-mysql php70w-fpm php70w-mbstring')
    os.system(php_ini)
    os.system("bash /tmp/php.sh")
    os.system('systemctl enable php-fpm.service')
    os.system('systemctl start php-fpm')

# 安装MySQL5.7
def install_mysql():
    os.system('yum -y install mysql-community-server')
    os.system('systemctl start mysqld')
    os.system('systemctl enable mysqld')
    with open('/tmp/mysqlpasswd.sh','w') as f:
        f.write(mysql_passwd)
    os.system('bash /tmp/mysqlpasswd.sh')
    
# nginx添加php配置
def nginxconf_php():
    with open('/etc/nginx/default.d/php.conf','w') as f:
        f.write(nginx_php)
    os.system('systemctl restart nginx')

# 检查lnmp搭建是否成功
def check_lnmp():
    res = requests.get('http://127.0.0.1/info.php').status_code
    return res

# 安装maccms
def install_maccms():
    os.system('cp -rf /usr/share/nginx/html /usr/share/nginx/html_bak')
    os.system('rm -rf /usr/share/nginx/html/*')
    os.system('wget -P /usr/share/nginx/html https://cdn.jsdelivr.net/gh/magicblack/maccms_down@master/maccms10.zip')
    os.system('cd /usr/share/nginx/html && unzip maccms10.zip')
    os.system('chmod -R 777 /usr/share/nginx/html')

if __name__ == "__main__":
    num = type_system()
    if int(num) == 2:
        try:
            firewalld()
            install()
            install_nginx()
            install_php()
            install_mysql()
            nginxconf_php()
        except:
            print('-----安装失败-----')
        os.system("echo '<?php phpinfo(); ?>' > /usr/share/nginx/html/info.php")
        code = check_lnmp()
        if int(code) == 200:
            install_maccms()
            print('----------部署成功----------')
            print('请访问http://127.0.0.1/index.php')
        else:
            print('----------LNMP平台部署失败----------')
    else:
        print("----------仅支持CentOS7版本----------")
