#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Author: André Pacheco
E-mail: pacheco.comp@gmail.com

This file contains the functions used to save and load trained model

If you find any bug or have some suggestion, please, email me.
"""

import torch
import os
import torch.nn as nn

def save_model (model, folder_path, epoch, opt_fn, loss_fn, is_best, multi_gpu=False, verbose=False):
    """
    This function saves the parameters of a model. It saves the last and best model (if it's the best).

    :param model (nn.Model): the model you wanna save the parameters
    :param folder_path (string): the folder you wanna save the checkpoints
    :param name_last (string): the file's name of the last checkpoint. Considers using epoch in the name
    :param name_best (bool, optional): the file's name of the best checkpoint. If it's False, it means this checkpoint
    :param verbose (bool, optional): If you'd like to print information on the screen. Default is False.
    is not the best one. Default is false.
    """

    last_check_path = os.path.join(folder_path, 'last-checkpoint')
    best_check_path = os.path.join(folder_path, 'best-checkpoint')

    if not os.path.exists(last_check_path):
        if verbose:
            print ('last-checkpoint folder does not exist. I am creating it!')
        os.mkdir(last_check_path)
    else:
        if verbose:
            print ('last-checkpoint folder exist! Perfect, I will just use it.')

    if not os.path.exists(best_check_path):
        if verbose:
            print('best-checkpoint folder does not exist. I am creating it!')
        os.mkdir(best_check_path)
    else:
        if verbose:
            print('best-checkpoint folder exist! Perfect, I will just use it.')

    info_to_save = {
        'epoch': epoch,
        'model_state_dict': model.module.state_dict() if multi_gpu else model.state_dict(),
        'optimizer_state_dict': opt_fn.state_dict(),
        'loss': loss_fn,
    }

    torch.save(info_to_save, os.path.join(last_check_path, "last-checkpoint.pth"))

    if is_best:
        torch.save(info_to_save, os.path.join(best_check_path, 'best-checkpoint.pth'))


def save_model_as_onnx (model, folder_path, name, input_data, input_names, 
                        output_names, dynamic_axes, use_parallel=False, verbose=False):
    """
    This function saves the model as onnx format.

    :param model (nn.Model): the model you wanna save the parameters
    :param folder_path (string): the folder you wanna save the checkpoints
    :param name (string): the file's name of the model. Considers using epoch in the name
    :param input_data (tuple): a single sample of all inputs of the model. For example: (img, metadata)
    :param input_names (list): the names of each input of the model. For example: ['img', 'metadata']
    :param output_names (list): the name of each output of the model. For example: ['output']
    :param dynamic_axes (dict): the dynamic axes of each data in input_names and output_names. 
                                For example: {'img': {0: 'batch_size'}, 
                                              'metadata': {0: 'batch_size'}, 
                                              'output': {0: 'batch_size'}
                                             }
    :param use_parallel (bool, optional): If the model was trained using DataParallel, you must set this 
                                          parameter as True. Default is False.
    :param verbose (bool, optional): If you'd like to print information on the screen. Default is False.
    """

    if not os.path.exists(folder_path):
        if verbose:
            print ('The folder {} does not exist. I am creating it!'.format(folder_path))
        os.mkdir(folder_path)
    else:
        if verbose:
            print ('The folder {} exist! Perfect, I will just use it.'.format(folder_path))

    model.eval()
    if use_parallel:
        model = model.module

    torch.onnx.export(model, 
                      input_data, 
                      os.path.join(folder_path, name),
                      input_names=input_names,
                      output_names=output_names,
                      dynamic_axes=dynamic_axes)


def load_model (checkpoint_path, model, opt_fn=None, loss_fn=None, epoch=None):
    """
    This function loads a model from a given checkpoint.

    :param checkpoint_path (string): the full path to de checkpoint
    :param model (nn.Model): the model that you wanna load the parameters
    :return (nn.Model): the loaded model
    """

    if not os.path.exists(checkpoint_path):
        raise Exception ("The {} does not exist!".format(checkpoint_path))

    ckpt = torch.load(checkpoint_path, weights_only=False)
    model.load_state_dict(ckpt['model_state_dict'])

    if opt_fn is not None and loss_fn is not None:
        opt_fn.load_state_dict(ckpt['optimizer_state_dict'])
        epoch = ckpt['epoch']
        loss_fn = ckpt['loss']
        return model, opt_fn, loss_fn, epoch
    else:
        return model

