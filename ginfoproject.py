#! /usr/bin/env python3
# coding: utf-8

from shutil import which, copyfile
import subprocess
import sys
import os

print("""   _____ _____        __        _____           _           _      _____                           _             
  / ____|_   _|      / _|      |  __ \\         (_)         | |    / ____|                         | |            
 | |  __  | |  _ __ | |_ ___   | |__) | __ ___  _  ___  ___| |_  | |  __  ___ _ __   ___ _ __ __ _| |_ ___  _ __ 
 | | |_ | | | | '_ \\|  _/ _ \\  |  ___/ '__/ _ \\| |/ _ \\/ __| __| | | |_ |/ _ \\ '_ \\ / _ \\ '__/ _` | __/ _ \\| '__|
 | |__| |_| |_| | | | || (_) | | |   | | | (_) | |  __/ (__| |_  | |__| |  __/ | | |  __/ | | (_| | || (_) | |   
  \\_____|_____|_| |_|_| \\___/  |_|   |_|  \\___/| |\\___|\\___|\\__|  \\_____|\\___|_| |_|\\___|_|  \\__,_|\\__\\___/|_|   
                                              _/ |                                                               
                                             |__/                                                                """)

TOOLS_NEEDED = ['php', 'composer', 'npm']

def add_after_in_file(filename, search, appendix):
    """ Adds 'appendix' in a file 'filename' after a line containing 'search'. """
    file = open(filename)
    content = file.read().split("\n")
    newcontent = []
    file.close()

    for line in content:
        newcontent.append(line)
        if search in line:
            newcontent.append(appendix)

    file2 = open(filename, 'w+')
    file2.write("\n".join(newcontent))
    file2.close()

def replace_line_in_file(filename, search, replaced):
    """ Replace a line containing 'search' by 'replaced' in a file 'filename'. """
    file = open(filename)
    content = file.read().split("\n")
    newcontent = []
    file.close()

    for line in content:
        if search in line:
            newcontent.append(replaced)
        else:
            newcontent.append(line)

    file2 = open(filename, 'w+')
    file2.write("\n".join(newcontent))
    file2.close()

def ask(name, check=None, default=None):
    """ Asks input to user until input is correct. """
    data = None
    while not data:
        data = input("[?] %s : " % (name+(' [%s] ' % default if default else '')))

        if not data:
            if default:
                data = default
            else:
                print("[!] Incorrect, try again.")

        if check:
            check_res = check(data)
            if not check_res[0]:
                data = None
                print("[!] Error : %s" % check_res[1])
            else:
                data = check_res[2]
                break
    return data


def check_project(data):
    """ Check function : project name """
    return (1 or not os.path.isdir(data), 'Folder %s already exists ' % data, data)


def check_yn(data):
    """ Check function : yes or no """
    if data.lower() in ['y', 'yes', 'o', 'oui']:
        return [1, '', 1]
    elif data.lower() in ['n', 'no', 'non']:
        return [1, '', 0]
    else:
        return [0, 'Enter yes or no', 0]


def print_title(title):
    """ Displays visible title in console """
    print()
    print('#'*(len(title)+6))
    print("#  %s  #" % title)
    print('#'*(len(title)+6))
    print()



def install_symfony(project_name, database_dsn):
    """
        Step 1 : Installing Symfony
        * Running composer command
        * Creating .env.local with database parameters
        * Creating database and first controller
    """
    print_title('Installing Symfony')

    # Initialize project
    subprocess.call(['composer', 'create-project', 'symfony/website-skeleton', project_name],
                    shell=True)
    os.chdir(project_name)

    # Create .env.local with proper DSN
    env_file = open('.env').read()
    open('.env.local', 'w+').write(
        env_file.replace('db_user:db_password@127.0.0.1:3306/db_name', database_dsn)
    )

    add_after_in_file('config/services.yaml', 'parameters:', "\n    locale: 'fr'")

    subprocess.call(['php', 'bin/console', 'doctrine:database:create'], shell=True)
    subprocess.call(['php', 'bin/console', 'make:controller', 'DefaultController'])


def install_fos_user():
    """
        Step 2 : Installing FOSUserBundle
        * Installing via composer
        * Adding configuratin files
        * Creating and executing database migeation
    """
    print_title('Installing FosUserBundle')

    # Installing from composer
    subprocess.call(['composer', 'require', 'friendsofsymfony/user-bundle', "~2.0"], shell=True)

    # Adding/editing config files
    copyfile(sys.path[0]+'/data/UserEntity.php', 'src/Entity/User.php')
    copyfile(sys.path[0]+'/data/security.yaml', 'config/packages/security.yaml')
    copyfile(sys.path[0]+'/data/fos_user.yaml', 'config/packages/fos_user.yaml')
    copyfile(sys.path[0]+'/data/fos_user_route.yaml', 'config/routes/fos_user.yaml')
    add_after_in_file('config/packages/framework.yaml', 'framework:', "    templating:\n        engines: ['twig', 'php']\n    ")

    # Making and executing migration
    subprocess.call(['php', 'bin/console', 'make:migration'], shell=True)
    subprocess.call(['php', 'bin/console', 'doctrine:migrations:migrate', '-n'], shell=True) # -n -> non interactive

    print('[+] FOSUserBundle installed.')


def install_mca_login(oauth):
    """
        Step 3 : Installing connection via MyCA
        * Installing OAuth module via composer
        * Updating .env (versionned) and .env.local (not versionned) with appropriate data.
        * Updating services.yaml to get ENV vars
        * Adding UserController with login via My
    """
    print_title('Adding MyCA login')

    subprocess.call(['composer', 'require', 'adoy/oauth2'], shell=True)


    add_after_in_file('.env.local',
                      '###< symfony/swiftmailer-bundle ###',
                      "\nOAUTH_BASE=%s\nOAUTH_ID=%s\nOAUTH_SECRET=%s" % oauth)
    add_after_in_file('.env',
                      '###< symfony/swiftmailer-bundle ###',
                      "\nOAUTH_BASE=%s\nOAUTH_ID=%s\nOAUTH_SECRET=" % oauth[:2])
    add_after_in_file('config/services.yaml',
                      'parameters:',
                      "    oauth_id: '%env(OAUTH_ID)%'\n    oauth_secret: '%env(OAUTH_SECRET)%'\n    oauth_base: '%env(OAUTH_BASE)%'")
    copyfile(sys.path[0]+'/data/UserController.php', 'src/Controller/UserController.php')

    print('[+] Added connection via MyCA.')

def install_webpack_encore():
    """ Step 4 : Installing Webpack Encore & JQuery """
    print_title('Adding Webpack')
    subprocess.call(['composer', 'require', 'symfony/webpack-encore-bundle'], shell=True)
    subprocess.call(['npm', 'install', '--save-dev', '@symfony/webpack-encore'], shell=True)
    subprocess.call(['npm', 'install', 'jquery'])

    print('[+] Webpack Encore & JQuery installed.')

def install_adminbsb():
    """ Step 5 : Installing AdminBSB & its dependences """
    print_title('Adding AdminBSB Material Design')
    subprocess.call([
        'npm', 'install', '-S',
        'bootstrap@3',
        'adminbsb-materialdesign',
        'animate.css',
        'bootstrap-notify',
        'bootstrap-select',
        'node-waves',
        'popper.js'
    ])

    copyfile(sys.path[0]+'/data/adminbsb/base.html.twig', 'templates/base.html.twig')
    copyfile(sys.path[0]+'/data/adminbsb/bootstrap_3_layout.html.twig', 'templates/form/bootstrap_3_layout.html.twig')
    copyfile(sys.path[0]+'/data/adminbsb/app.js', 'assets/js/app.js')
    copyfile(sys.path[0]+'/data/adminbsb/vendor.js', 'assets/js/vendor.js')
    copyfile(sys.path[0]+'/data/adminbsb/app.scss', 'assets/css/app.scss')

    add_after_in_file('webpack.config.js',
                      ".addEntry('app', './assets/js/app.js')",
                      "    .createSharedEntry('vendor', './assets/js/vendor.js')")

    replace_line_in_file('webpack.config.js',
                         '    //.enableSassLoader()',
                         '    .enableSassLoader()')

    replace_line_in_file('webpack.config.js',
                         '    //.autoProvidejQuery()',
                         '    .autoProvidejQuery()')

    subprocess.call(['npm', 'run', 'build'])

    print('[+] Initialized AdminBSB template')



def check_main_depencies():
    """ Check if dependencies listed in TOOLS_NEEDED are installed """
    print("# Checking dependencies")
    for tool in TOOLS_NEEDED:
        print("[+] Checking %s... " % tool, end='')
        if which(tool) is not None:
            print("ok!")
        else:
            print("missing!")
            sys.exit()

    print()
    print("[+] Dependencies ok !")
    print()


def main():
    """ Main function, checking dependencies and doing the thing. """
    # Checking if dependencies are installed
    check_main_depencies()

    project_name = ask('Project name', check_project)
    use_fosuser = ask('Install FosUserBundle (y/n)', check_yn, 'y')

    default_dsn = 'root:@127.0.0.1:3306' if os.name != 'posix' else 'root:root@127.0.0.1:3306'
    default_dsn += '/%s' % project_name
    database_dsn = ask('Database DSN', None, default_dsn)

    if use_fosuser:
        use_mca = ask('Add MyCentraleAssos login process (y/n)', check_yn, 'y')

        if use_mca:
            oauth_base = ask('OAuth Base', None, 'https://my.centrale-assos.fr')
            oauth_id = ask('OAuth ID', None, '3_')
            oauth_secret = ask('OAuth Secret')
    else:
        use_mca = False

    use_encore = ask('Install Webpack Encore (y/n)', check_yn, 'y')

    if use_encore:
        use_adminbsb = ask('Install AdminBSB theme (y/n)', check_yn, 'y')
    else:
        use_adminbsb = False


    install_symfony(project_name, database_dsn)
    if use_fosuser:
        install_fos_user()
    if use_mca:
        install_mca_login((oauth_base, oauth_id, oauth_secret))
    if use_encore:
        install_webpack_encore()
    if use_adminbsb:
        install_adminbsb()

    subprocess.call(['php', 'bin/console', 'cache:clear', '--env=dev'], shell=True)


if __name__ == '__main__':
    main()
