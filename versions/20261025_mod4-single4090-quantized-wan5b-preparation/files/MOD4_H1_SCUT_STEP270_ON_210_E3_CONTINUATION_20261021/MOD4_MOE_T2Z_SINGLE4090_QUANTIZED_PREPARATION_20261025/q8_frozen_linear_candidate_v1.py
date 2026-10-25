"""Uninstalled Q8_0 frozen-weight autograd prototype; not a full Wan/T2-z loader.

GGUF Q8_0 blocks contain little-endian fp16 scale plus32 signed int8 values.
Recomputing dequantization in backward avoids retaining a dense weight copy
per layer. Only input gradients are provided: this path cannot full-finetune DiT.
"""
import torch
from torch import nn
import torch.nn.functional as F

def dequantize_q8_0(blocks,shape,dtype):
    if blocks.dtype!=torch.uint8 or blocks.ndim!=2 or blocks.shape[1]!=34:
        raise ValueError('Expected Q8_0 packed blocks with34 bytes')
    if len(shape)!=2 or shape[0]*shape[1]!=len(blocks)*32:
        raise ValueError('Expected exact divisible32 linear weight shape')
    scale=blocks[:,:2].contiguous().view(torch.float16).to(dtype)
    values=blocks[:,2:].contiguous().view(torch.int8).to(dtype)
    return (scale*values).reshape(shape)

class _FrozenQ8InputGradient(torch.autograd.Function):
    @staticmethod
    def forward(ctx,x,blocks,bias,rows,columns):
        ctx.save_for_backward(blocks);ctx.shape=(rows,columns);ctx.compute_dtype=x.dtype
        weight=dequantize_q8_0(blocks,ctx.shape,x.dtype)
        return F.linear(x,weight,bias)
    @staticmethod
    def backward(ctx,gradient):
        blocks,=ctx.saved_tensors
        weight=dequantize_q8_0(blocks,ctx.shape,ctx.compute_dtype)
        return gradient.matmul(weight),None,None,None,None

class FrozenQ8Linear(nn.Module):
    def __init__(self,blocks,shape,bias=None):
        super().__init__();self.shape=tuple(shape)
        if len(self.shape)!=2:raise ValueError('Linear weight must be2D')
        self.register_buffer('q8_blocks',blocks.detach().clone())
        self.register_buffer('bias',None if bias is None else bias.detach().clone())
    def forward(self,x):
        if x.shape[-1]!=self.shape[1]:raise ValueError('Linear input dimension mismatch')
        return _FrozenQ8InputGradient.apply(x,self.q8_blocks,self.bias,*self.shape)
