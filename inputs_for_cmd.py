#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Run this file for starting the Chess game.
"""

# import one code:
import helper

if __name__ == '__main__':
    try:
        helper.inputs_for_cmd()

    except BrokenPipeError or ConnectionError or Exception or ValueError as err:
        print(f'Something went real wrong. Error: {err}')
