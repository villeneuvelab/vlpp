#!/usr/bin/env python
# -*- coding: utf-8 -*-


from vlpp.realign import Realign


def main():

    pet = "${pet}"

    params = {
        "petPath": "${pet}",
        "dataset": "${dataset}",
        "ignore": "${realignParams.ignore}",
    }

    realign = Realign(**params)
    realign.run()


if __name__ == '__main__':
    main()
