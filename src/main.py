from libeconf import libeconf


def main():
    file_name: bytes = b'./example.conf'
    delim: bytes = b'='
    comment: bytes = b'#'
    config = libeconf.econf_readFile(file_name, delim, comment)
    return config


if __name__ == "__main__":
    main()
