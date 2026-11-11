"""Genuine refinements of the existing staged optimizer, without GT access.

`continued` adds optimization from its final parameters with a smaller step.
`mobility_correction` restores the paper's Stage 3(c): fix articulation and
minimize cross-mobile geometric inconsistency over mobility alone (Eq. 15).
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
import torch
import torch.nn.functional as F
from lightweight_splart import camera_matrices, render_density, cross_mobile_sets, weighted_chamfer


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--mode',choices=['continued','mobility_correction'],required=True)
    parser.add_argument('--input',required=True)
    parser.add_argument('--output',required=True)
    args=parser.parse_args()
    torch.set_num_threads(1)
    initial=json.loads(Path(args.input).read_text())
    results=[]
    for row in initial['results']:
        with np.load(Path('data/synthetic_splart')/(row['scene']+'.npz')) as data:
            x0=torch.tensor(data['state0'],dtype=torch.float32)
            x1=torch.tensor(data['state1'],dtype=torch.float32)
            opacity=torch.tensor(data['opacities'],dtype=torch.float32)
            kind=str(data['articulation_type'])
        logits=[torch.logit(torch.tensor(row[k],dtype=torch.float32).clamp(1e-6,1-1e-6)).requires_grad_()
                for k in ['mobility_state0','mobility_state1']]
        axis=torch.tensor(row['axis'],dtype=torch.float32)
        amount=torch.tensor(row['amount'],dtype=torch.float32)
        pivot=torch.tensor(row['pivot'],dtype=torch.float32)
        params=list(logits)
        if args.mode=='continued':
            params.extend([axis.requires_grad_(),amount.requires_grad_()])
            if kind=='revolute': params.append(pivot.requires_grad_())
            cameras=camera_matrices('cpu')
            target0=render_density(x0,opacity,cameras)
            target1=render_density(x1,opacity,cameras)
        opt=torch.optim.Adam(params,lr=.003 if args.mode=='continued' else .1)
        steps=840 if args.mode=='continued' else 500
        print(row['scene'],args.mode,'start',flush=True)
        for i in range(steps):
            if args.mode=='continued':
                fraction=max(0.,(i-420)/max(steps-421,1))
                for group in opt.param_groups: group['lr']=.003*(.05**fraction)
            m0,m1=[torch.sigmoid(l) for l in logits]
            ax=F.normalize(axis,dim=0)
            a,wa=cross_mobile_sets(x0,x1,opacity,m0,m1,kind,ax,pivot,amount,0)
            b,wb=cross_mobile_sets(x0,x1,opacity,m0,m1,kind,ax,pivot,amount,1)
            loss=weighted_chamfer(a,wa,x0,opacity)+weighted_chamfer(b,wb,x1,opacity)
            if args.mode=='continued':
                loss=loss+.25*F.mse_loss(render_density(a,wa,cameras),target0)
                loss=loss+.25*F.mse_loss(render_density(b,wb,cameras),target1)
                loss=loss+.03*F.mse_loss(m0,m1)
            opt.zero_grad()
            loss.backward()
            opt.step()
        with torch.no_grad():
            row.update(axis=F.normalize(axis,dim=0).tolist(),amount=float(amount),pivot=pivot.tolist(),
                       mobility_state0=torch.sigmoid(logits[0]).tolist(),mobility_state1=torch.sigmoid(logits[1]).tolist(),
                       self_supervised_loss=float(loss))
        print(row['scene'],'final loss',float(loss),flush=True)
        results.append(row)
    Path(args.output).write_text(json.dumps({'method':'refined','results':results},indent=2))


if __name__=='__main__': main()
