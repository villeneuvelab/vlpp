#!/usr/bin/env python
# -*- coding: utf-8 -*-


from vlpp.operation import maskFromAtlas


def main():
    output = "${participant}_roi-${refName}${suffix.mask}"
    maskFromAtlas("${atlas}", ${indices}, output)


if __name__ == '__main__':
    main()
