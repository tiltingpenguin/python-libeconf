from libeconf import libeconf


def main():
    file_name: bytes = b'./test.conf'
    delim: bytes = b'='
    comment: bytes = b'#'
    config = libeconf.econf_readFile(file_name, delim, comment)
    # print("get_path", libeconf.econf_getPath(config))
    groups = libeconf.econf_getGroups(config)
    libeconf.econf_getKeys(config)
    # libeconf.econf_getIntValue(config, b'[Group]', b'Bla')


if __name__ == "__main__":
    main()
