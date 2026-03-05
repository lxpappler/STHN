import numpy as np
import os
import json
import torch
import argparse
from model.network import STHN
from utils import save_overlap_img, save_img, setup_seed, save_overlap_bbox_img
import datasets_4cor_img as datasets
import scipy.io as io
import torchvision
import numpy as np
import time
from tqdm import tqdm
import cv2
import kornia.geometry.transform as tgm
import matplotlib.pyplot as plt
from plot_hist import plot_hist_helper
import torch.nn.functional as F
import parser
from datetime import datetime
from os.path import join
import commons
import logging
import wandb

def _init_diag_state():
    return {
        "coarse": {},
        "fine": {},
        "corr_maps": {"coarse": [], "fine": []},
        "num_batches": 0,
    }


def _update_diag_state(diag_state, model_debug_outputs, args, batch_idx):
    if not model_debug_outputs:
        return

    for stage_name in ["coarse", "fine"]:
        stage_data = model_debug_outputs.get(stage_name)
        if stage_data is None:
            continue

        for record in stage_data.get("trace", []):
            itr = int(record.get("iter", -1))
            if itr < 0:
                continue
            stage_bucket = diag_state[stage_name].setdefault(itr, {
                "corr_entropy": [],
                "corr_peak_rel_margin": [],
                "corr_multipeak_ratio": [],
                "corr_std": [],
                "delta_norm": [],
                "delta_cosine": [],
                "delta_flip_ratio": [],
            })
            for key in stage_bucket.keys():
                val = float(record.get(key, float("nan")))
                if np.isfinite(val):
                    stage_bucket[key].append(val)

        if batch_idx < args.diag_save_map_batches:
            for corr_map_obj in stage_data.get("corr_maps", []):
                if len(diag_state["corr_maps"][stage_name]) >= args.diag_save_map_batches:
                    break
                diag_state["corr_maps"][stage_name].append(corr_map_obj)


def _plot_diag_curves(stage_name, stage_bucket, save_dir):
    if not stage_bucket:
        return {}

    sorted_iters = sorted(stage_bucket.keys())
    summary = {}
    for metric in [
        "corr_entropy",
        "corr_peak_rel_margin",
        "corr_multipeak_ratio",
        "corr_std",
        "delta_norm",
        "delta_cosine",
        "delta_flip_ratio",
    ]:
        ys = []
        for itr in sorted_iters:
            vals = stage_bucket[itr][metric]
            ys.append(float(np.mean(vals)) if len(vals) > 0 else float("nan"))

        summary[metric] = ys
        if np.all(np.isnan(np.array(ys))):
            continue

        plt.figure(figsize=(6, 4))
        plt.plot(sorted_iters, ys, marker="o")
        plt.xlabel("Iteration")
        plt.ylabel(metric)
        plt.title(f"{stage_name}: {metric}")
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(os.path.join(save_dir, f"diag_{stage_name}_{metric}.png"))
        plt.close()

    summary["iters"] = sorted_iters
    return summary


def _save_corr_maps(diag_state, save_dir):
    for stage_name in ["coarse", "fine"]:
        for idx, corr_map_obj in enumerate(diag_state["corr_maps"][stage_name]):
            corr_map = np.array(corr_map_obj["map"], dtype=np.float32)
            itr = corr_map_obj.get("iter", -1)

            plt.figure(figsize=(4, 4))
            plt.imshow(corr_map, cmap="viridis")
            plt.colorbar()
            plt.title(f"{stage_name} corr map (iter={itr})")
            plt.tight_layout()
            plt.savefig(os.path.join(save_dir, f"diag_{stage_name}_corrmap_{idx:02d}_iter{itr}.png"))
            plt.close()


def _diagnose_bottleneck(diag_summary, args):
    coarse = diag_summary.get("coarse", {})
    entropy = np.array(coarse.get("corr_entropy", []), dtype=np.float32)
    peak_margin = np.array(coarse.get("corr_peak_rel_margin", []), dtype=np.float32)
    multipeak = np.array(coarse.get("corr_multipeak_ratio", []), dtype=np.float32)
    delta_flip = np.array(coarse.get("delta_flip_ratio", []), dtype=np.float32)

    mean_entropy = float(np.nanmean(entropy)) if entropy.size else float("nan")
    mean_peak_margin = float(np.nanmean(peak_margin)) if peak_margin.size else float("nan")
    mean_multipeak = float(np.nanmean(multipeak)) if multipeak.size else float("nan")
    mean_flip = float(np.nanmean(delta_flip)) if delta_flip.size else float("nan")

    feature_bottleneck = (
        np.isfinite(mean_entropy)
        and np.isfinite(mean_peak_margin)
        and np.isfinite(mean_multipeak)
        and mean_entropy >= args.diag_entropy_thr
        and mean_peak_margin <= args.diag_peak_margin_thr
        and mean_multipeak >= args.diag_multipeak_thr
    )

    iterative_bottleneck = (
        np.isfinite(mean_peak_margin)
        and np.isfinite(mean_entropy)
        and np.isfinite(mean_flip)
        and mean_peak_margin > args.diag_peak_margin_thr
        and mean_entropy < args.diag_entropy_thr
        and mean_flip >= args.diag_flip_thr
    )

    if feature_bottleneck:
        verdict = "feature_extractor_bottleneck"
    elif iterative_bottleneck:
        verdict = "iterative_updater_bottleneck"
    else:
        verdict = "inconclusive"

    return {
        "verdict": verdict,
        "mean_corr_entropy": mean_entropy,
        "mean_corr_peak_rel_margin": mean_peak_margin,
        "mean_corr_multipeak_ratio": mean_multipeak,
        "mean_delta_flip_ratio": mean_flip,
        "thresholds": {
            "diag_entropy_thr": args.diag_entropy_thr,
            "diag_peak_margin_thr": args.diag_peak_margin_thr,
            "diag_multipeak_thr": args.diag_multipeak_thr,
            "diag_flip_thr": args.diag_flip_thr,
        },
    }


def _finalize_diag(diag_state, args):
    diag_dir = os.path.join(args.save_dir, "diagnostics")
    os.makedirs(diag_dir, exist_ok=True)

    diag_summary = {
        "coarse": _plot_diag_curves("coarse", diag_state["coarse"], diag_dir),
        "fine": _plot_diag_curves("fine", diag_state["fine"], diag_dir),
    }
    _save_corr_maps(diag_state, diag_dir)

    diagnosis = _diagnose_bottleneck(diag_summary, args)
    payload = {
        "num_batches": diag_state["num_batches"],
        "diagnosis": diagnosis,
        "summary": diag_summary,
    }

    with open(os.path.join(diag_dir, "diagnosis_report.json"), "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    logging.info(f"Diagnostic verdict: {diagnosis['verdict']}")
    logging.info(
        f"Diagnostic means -> entropy={diagnosis['mean_corr_entropy']:.4f}, "
        f"peak_margin={diagnosis['mean_corr_peak_rel_margin']:.4f}, "
        f"multipeak={diagnosis['mean_corr_multipeak_ratio']:.4f}, "
        f"delta_flip={diagnosis['mean_delta_flip_ratio']:.4f}"
    )


def test(args, wandb_log):
    if not args.identity:
        model = STHN(args)
        if not args.train_ue_method == "train_only_ue_raw_input":
            model_med = torch.load(args.eval_model, map_location='cuda:0')
            for key in list(model_med['netG'].keys()):
                model_med['netG'][key.replace('module.','')] = model_med['netG'][key]
            for key in list(model_med['netG'].keys()):
                if key.startswith('module'):
                    del model_med['netG'][key]
            model.netG.load_state_dict(model_med['netG'], strict=False)
        if args.use_ue:
            if args.eval_model_ue is not None:
                model_med = torch.load(args.eval_model_ue, map_location='cuda:0')
            for key in list(model_med['netD'].keys()):
                model_med['netD'][key.replace('module.','')] = model_med['netD'][key]
            for key in list(model_med['netD'].keys()):
                if key.startswith('module'):
                    del model_med['netD'][key]
            model.netD.load_state_dict(model_med['netD'])
        if args.two_stages:
            if args.eval_model_fine is None:
                model_med = torch.load(args.eval_model, map_location='cuda:0')
                for key in list(model_med['netG_fine'].keys()):
                    model_med['netG_fine'][key.replace('module.','')] = model_med['netG_fine'][key]
                for key in list(model_med['netG_fine'].keys()):
                    if key.startswith('module'):
                        del model_med['netG_fine'][key]
                model.netG_fine.load_state_dict(model_med['netG_fine'])
            else:
                model_med = torch.load(args.eval_model_fine, map_location='cuda:0')
                for key in list(model_med['netG'].keys()):
                    model_med['netG'][key.replace('module.','')] = model_med['netG'][key]
                for key in list(model_med['netG'].keys()):
                    if key.startswith('module'):
                        del model_med['netG'][key]
                model.netG_fine.load_state_dict(model_med['netG'], strict=False)
        
        model.setup() 
        model.netG.eval()
        if args.use_ue:
            model.netD.eval()
        if args.two_stages:
            model.netG_fine.eval()
    else:
        model = None
    if args.test:
        val_dataset = datasets.fetch_dataloader(args, split='test')
    else:
        val_dataset = datasets.fetch_dataloader(args, split='val')
    evaluate_SNet(model, val_dataset, batch_size=args.batch_size, args=args, wandb_log=wandb_log)
    
def evaluate_SNet(model, val_dataset, batch_size=0, args = None, wandb_log=False):

    assert batch_size > 0, "batchsize > 0"

    total_mace = torch.empty(0)
    total_flow = torch.empty(0)
    total_ce =torch.empty(0)
    total_mace_conf_error = torch.empty(0)
    timeall=[]
    mace_conf_list = []
    if args.generate_test_pairs:
        test_pairs = torch.zeros(len(val_dataset.dataset), dtype=torch.long)

    diag_state = _init_diag_state() if args.diagnose_corr else None

    for i_batch, data_blob in enumerate(tqdm(val_dataset)):
        if args.diagnose_corr and i_batch >= args.diag_batches:
            break
        img1, img2, flow_gt, H, query_utm, database_utm, index, pos_index = [x for x in data_blob]
        if args.generate_test_pairs:
            test_pairs[index] = pos_index

        if i_batch == 0:
            logging.info("Check the reproducibility by UTM:")
            logging.info(f"the first 5th query UTMs: {query_utm[:5]}")
            logging.info(f"the first 5th database UTMs: {database_utm[:5]}")

        if i_batch%1000 == 0:
            save_img(torchvision.utils.make_grid((img1)),
                     args.save_dir + "/b1_epoch_" + str(i_batch).zfill(5) + "_finaleval_" + '.png')
            save_img(torchvision.utils.make_grid((img2)),
                     args.save_dir + "/b2_epoch_" + str(i_batch).zfill(5) + "_finaleval_" + '.png')

        if not args.identity:
            model.set_input(img1, img2, flow_gt)
            flow_4cor = torch.zeros((flow_gt.shape[0], 2, 2, 2))
            flow_4cor[:, :, 0, 0] = flow_gt[:, :, 0, 0]
            flow_4cor[:, :, 0, 1] = flow_gt[:, :, 0, -1]
            flow_4cor[:, :, 1, 0] = flow_gt[:, :, -1, 0]
            flow_4cor[:, :, 1, 1] = flow_gt[:, :, -1, -1]
            flow_ = (flow_4cor)**2
            flow_ = ((flow_[:,0,:,:] + flow_[:,1,:,:])**0.5)
            flow_vec = torch.mean(torch.mean(flow_, dim=1), dim=1)

        if args.train_ue_method != 'train_only_ue_raw_input':
            if not args.identity:
                # time_start = time.time()
                model.forward()
                if args.diagnose_corr:
                    _update_diag_state(diag_state, getattr(model, 'debug_outputs', {}), args, i_batch)
                    diag_state['num_batches'] += 1
                # time_end = time.time()
                four_pred = model.four_pred
                # timeall.append(time_end-time_start)
                # print(time_end-time_start)
            else:
                four_pred = torch.zeros((flow_gt.shape[0], 2, 2, 2))

            alpha = args.database_size / args.resize_width
            mace_ = (flow_4cor - four_pred.cpu().detach())**2
            mace_ = ((mace_[:,0,:,:] + mace_[:,1,:,:])**0.5)
            mace_vec = torch.mean(torch.mean(mace_, dim=1), dim=1)
            mace_vec = mace_vec * alpha
            # print(mace_[0,:])

            total_mace = torch.cat([total_mace,mace_vec], dim=0)
            final_mace = torch.mean(total_mace).item()
            total_flow = torch.cat([total_flow,flow_vec], dim=0)
            final_flow = torch.mean(total_flow).item()
            
            # CE
            four_point_org_single = torch.zeros((1, 2, 2, 2))
            four_point_org_single[:, :, 0, 0] = torch.Tensor([0, 0])
            four_point_org_single[:, :, 0, 1] = torch.Tensor([args.resize_width - 1, 0])
            four_point_org_single[:, :, 1, 0] = torch.Tensor([0, args.resize_width - 1])
            four_point_org_single[:, :, 1, 1] = torch.Tensor([args.resize_width - 1, args.resize_width - 1])
            four_point_1 = four_pred.cpu().detach() + four_point_org_single
            four_point_org = four_point_org_single.repeat(four_point_1.shape[0],1,1,1).flatten(2).permute(0, 2, 1).contiguous() 
            four_point_1 = four_point_1.flatten(2).permute(0, 2, 1).contiguous()
            four_point_gt = flow_4cor.cpu().detach() + four_point_org_single
            four_point_gt = four_point_gt.flatten(2).permute(0, 2, 1).contiguous()
            H = tgm.get_perspective_transform(four_point_org, four_point_1)
            center_T = torch.tensor([args.resize_width/2-0.5, args.resize_width/2-0.5, 1]).unsqueeze(1).unsqueeze(0).repeat(H.shape[0], 1, 1)
            w = torch.bmm(H, center_T).squeeze(2)
            center_pred_offset = w[:, :2]/w[:, 2].unsqueeze(1) - center_T[:, :2].squeeze(2)
            H_gt = tgm.get_perspective_transform(four_point_org, four_point_gt)
            w_gt = torch.bmm(H_gt, center_T).squeeze(2)
            center_gt_offset = w_gt[:, :2]/w_gt[:, 2].unsqueeze(1) - center_T[:, :2].squeeze(2)
            ce_ = (center_pred_offset - center_gt_offset)**2
            ce_ = ((ce_[:,0] + ce_[:,1])**0.5)
            ce_vec = ce_
            ce_vec = ce_vec * alpha
            total_ce = torch.cat([total_ce, ce_vec], dim=0)
            final_ce = torch.mean(total_ce).item()
            
            if args.vis_all:
                save_dir = os.path.join(args.save_dir, 'vis')
                if not os.path.exists(save_dir):
                    os.mkdir(save_dir)
                if not args.two_stages:
                    save_overlap_bbox_img(img1, model.fake_warped_image_2, save_dir + f'/train_overlap_bbox_{i_batch}.png', four_point_gt, four_point_1)
                else:
                    four_point_org_single_ori = torch.zeros((1, 2, 2, 2))
                    four_point_org_single_ori[:, :, 0, 0] = torch.Tensor([0, 0])
                    four_point_org_single_ori[:, :, 0, 1] = torch.Tensor([args.database_size - 1, 0])
                    four_point_org_single_ori[:, :, 1, 0] = torch.Tensor([0, args.database_size - 1])
                    four_point_org_single_ori[:, :, 1, 1] = torch.Tensor([args.database_size - 1, args.database_size - 1])
                    four_point_bbox = model.flow_bbox.cpu().detach() + four_point_org_single_ori
                    alpha = args.database_size / args.resize_width
                    four_point_bbox = four_point_bbox.flatten(2).permute(0, 2, 1).contiguous() / alpha
                    save_overlap_bbox_img(img1, model.fake_warped_image_2, save_dir + f'/train_overlap_bbox_{i_batch}.png', four_point_gt, four_point_1, crop_bbox=four_point_bbox)
                
        if not args.identity:
            if args.use_ue:
                with torch.no_grad():
                    conf_pred = model.predict_uncertainty(GAN_mode=args.GAN_mode)
                conf_vec = torch.mean(conf_pred, dim=[1, 2, 3])
                if args.GAN_mode == "macegan" and args.D_net != "ue_branch":
                    logging.debug(f"conf_pred_diff:{conf_vec.cpu() - torch.exp(args.ue_alpha * mace_vec)}.")
                    logging.debug(f"pred_mace:{mace_vec}")
                    mace_conf_error_vec = F.l1_loss(conf_vec.cpu(), torch.exp(args.ue_alpha * mace_vec))
                elif args.GAN_mode == "vanilla_rej":
                    flow_bool = torch.ones_like(flow_vec)
                    alpha = args.database_size / args.resize_width
                    flow_bool[flow_vec >= (args.rej_threshold / alpha)] = 0.0
                    mace_conf_error_vec = F.binary_cross_entropy(conf_vec.cpu(), flow_bool) # sigmoid in predict uncertainty
                total_mace_conf_error = torch.cat([total_mace_conf_error, mace_conf_error_vec.reshape(1)], dim=0)
                final_mace_conf_error = torch.mean(total_mace_conf_error).item()
                if args.GAN_mode == "macegan" and args.D_net != "ue_branch":
                    for i in range(len(mace_vec)):
                        mace_conf_list.append((mace_vec[i].item(), conf_vec[i].item()))
                elif args.GAN_mode == "vanilla_rej":
                    for i in range(len(flow_vec)):
                        mace_conf_list.append((flow_vec[i].item(), conf_vec[i].item()))

    if not args.train_ue_method == "train_only_ue_raw_input":
        logging.info(f"MACE Metric: {final_mace}")
        logging.info(f'CE Metric: {final_ce}')
        print(f"MACE Metric: {final_mace}")
        print(f'CE Metric: {final_ce}')
        if wandb_log:
            wandb.log({"test_mace": final_mace})
            wandb.log({"test_ce": final_ce})
    if args.use_ue:
        mace_conf_list = np.array(mace_conf_list)
        # plot mace conf
        plt.figure()
        # plt.axis('equal')
        plt.scatter(mace_conf_list[:,0], mace_conf_list[:,1], s=1)
        x = np.linspace(0, 100, 400)
        y = np.exp(args.ue_alpha * x)
        plt.plot(x, y, label='f(x) = exp(-0.1x)', color='red')
        plt.legend()
        plt.savefig(args.save_dir + f'/final_conf.png')
        plt.close()
        plt.figure()
        n, bins, patches = plt.hist(x=mace_conf_list[:,1], bins=np.linspace(0, 1, 20))
        logging.info(n)
        plt.close()
        logging.info(f"MACE CONF ERROR Metric: {final_mace_conf_error}")
        if wandb_log:
            wandb.log({"test_mace_conf_error": final_mace_conf_error})
    logging.info(np.mean(np.array(timeall[1:-1])))
    io.savemat(args.save_dir + '/resmat', {'matrix': total_mace.numpy()})
    np.save(args.save_dir + '/resnpy.npy', total_mace.numpy())
    io.savemat(args.save_dir + '/flowmat', {'matrix': total_flow.numpy()})
    np.save(args.save_dir + '/flownpy.npy', total_flow.numpy())

    if args.diagnose_corr:
        _finalize_diag(diag_state, args)

    plot_hist_helper(args.save_dir)

if __name__ == '__main__':
    args = parser.parse_arguments()
    start_time = datetime.now()
    if args.identity:
        pass
    else:
        args.save_dir = join(
        "test",
        args.save_dir,
        args.eval_model.split("/")[-2] if args.eval_model is not None else args.eval_model_ue.split("/")[-2],
        f"{args.dataset_name}-{start_time.strftime('%Y-%m-%d_%H-%M-%S')}",
        )
        commons.setup_logging(args.save_dir, console='info')
    setup_seed(0)
    logging.debug(args)
    wandb_log = True
    if wandb_log:
        wandb.init(project="STHN-eval", entity="xjh19971", config=vars(args))
    test(args, wandb_log)



