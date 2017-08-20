#!/usr/bin/env python2

import argparse
import os
import random

import argconfig
import docker
import shuffle
import version


cuda_cudnn_choices = [
    (cuda, cudnn) for cuda, cudnn in docker.cuda_cudnn_choices
    if cuda != 'none']

cupy_major = version.get_cupy_version()[0]

if cupy_major <= 1:
    cuda_cudnn = [
        (cuda, cudnn) for cuda, cudnn in cuda_cudnn_choices
        if cuda != 'cuda90' and 'cudnn7' not in cudnn]
else:
    cuda_cudnn = docker.cuda_cudnn_choices


params = {
    'base': docker.base_choices,
    'cuda_cudnn': cuda_cudnn_choices,
    'nccl': docker.nccl_choices,
    'numpy': ['1.9', '1.10', '1.11', '1.12'],
    'scipy': [None, '0.18'],
}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Test script for multi-environment')
    parser.add_argument('--id', type=int, required=True)
    parser.add_argument('--no-cache', action='store_true')
    parser.add_argument('--timeout', default='1h')
    parser.add_argument('--interactive', action='store_true')
    argconfig.setup_argument_parser(parser)
    args = parser.parse_args()

    conf = shuffle.make_shuffle_conf(params, args.id)
    conf['requires'] = [
        'setuptools',
        'pip',
        'cython==0.24'
    ] + conf['requires'] + [
        'nose',
        'mock',
        'coverage',
        'coveralls',
    ]

    volume = []
    env = {'CUDNN': conf['cudnn']}

    argconfig.parse_args(args, env, conf, volume)
    argconfig.set_coveralls(args, env)

    if args.interactive:
        docker.run_interactive(
            conf, no_cache=args.no_cache, volume=volume, env=env)
    else:
        docker.run_with(
            conf, './test_cupy.sh', no_cache=args.no_cache, volume=volume,
            env=env, timeout=args.timeout, gpu_id=args.gpu_id)
