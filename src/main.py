from libeconf import libeconf


def main():
    file_name = b"/home/nkrapp/test.conf"
    delim = b"="
    comment = b"#"
    config = libeconf.econf_readFile(file_name, delim, comment)
    libeconf.econf_getIntValue(config, b"Group", b"Bla")


if __name__ == "__main__":
    main()
