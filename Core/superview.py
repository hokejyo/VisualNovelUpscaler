# -*- coding: utf-8 -*-

import sys
import math

# modified from https://intofpv.com/t-using-free-command-line-sorcery-to-fake-superview


def derp_it(tx, target_width, src_width):
    x = (float(tx) / target_width - 0.5) * 2  # -1 -> 1
    sx = tx - (target_width - src_width) / 2
    offset = math.pow(x, 2) * (-1 if x < 0 else 1) * ((target_width - src_width) / 2)
    return sx - offset


def go():
    target_width = int(sys.argv[1])
    height = int(sys.argv[2])
    src_width = int(sys.argv[3])

    xmap = open('xmap.pgm', 'w')
    xmap.write('P2 {0} {1} 65535\n'.format(target_width, height))

    for y in range(height):
        for x in range(target_width):
            fudgeit = derp_it(x, target_width, src_width)
            xmap.write('{0} '.format(int(fudgeit)))
        xmap.write('\n')

    xmap.close()

    ymap = open('ymap.pgm', 'w')
    ymap.write('P2 {0} {1} 65535\n'.format(target_width, height))

    for y in range(height):
        for x in range(target_width):
            ymap.write('{0} '.format(y))
        ymap.write('\n')

    ymap.close()


if __name__ == '__main__':
    go()
