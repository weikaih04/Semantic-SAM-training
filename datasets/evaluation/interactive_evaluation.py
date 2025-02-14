# Copyright (c) Facebook, Inc. and its affiliates.
import logging

import numpy as np
import torch
from torchvision.ops import box_iou

from detectron2.structures import BoxMode
from detectron2.data import MetadataCatalog
from detectron2.utils.comm import all_gather, gather, is_main_process, synchronize
from detectron2.evaluation.evaluator import DatasetEvaluator

import os
import time
from datetime import datetime
import json

class JointBoxPointInteractiveEvaluator(DatasetEvaluator):
    def __init__(
            self,
            dataset_name,
            output_dir,
            max_clicks=20,
            iou_iter=1,
            compute_box=False,
            distributed=True,
            box_interactive=False,
    ):
        self.box_interactive = box_interactive
        if box_interactive:
            self.box_evaluator = InteractiveEvaluator(dataset_name,
                                                      output_dir,
                                                      max_clicks=max_clicks,
                                                      iou_iter=iou_iter,
                                                      compute_box=compute_box,
                                                      distributed=distributed, )
        self.point_evaluator = InteractiveEvaluator(dataset_name,
                                                  output_dir,
                                                  max_clicks=max_clicks,
                                                  iou_iter=iou_iter,
                                                  compute_box=compute_box,
                                                  distributed=distributed, )
        self.point_evaluator_oracle = InteractiveEvaluator(dataset_name,
                                                    output_dir,
                                                    max_clicks=max_clicks,
                                                    iou_iter=iou_iter,
                                                    compute_box=compute_box,
                                                    distributed=distributed, )

    def reset(self):
        if self.box_interactive:
            self.box_evaluator.reset()
        self.point_evaluator.reset()
        self.point_evaluator_oracle.reset()

    def process(self, inputs, outputs):
        if self.box_interactive:
            self.box_evaluator.process(inputs, outputs['box'])
            point_out = outputs['point']
        else:
            point_out = outputs
        self.point_evaluator.process(inputs, point_out['max'])
        self.point_evaluator_oracle.process(inputs, point_out['oracle'])

    def evaluate(self):
        if self.box_interactive:
            print("evaluate box interactive")
            self.box_evaluator.evaluate()
        print("evaluate point interactive max iou socre")
        self.point_evaluator.evaluate()
        print("evaluate point interactive oracle")
        self.point_evaluator_oracle.evaluate()

class InteractiveEvaluator(DatasetEvaluator):
    """
    Evaluate point interactive IoU metrics.
    """

    def __init__(
            self,
            dataset_name,
            output_dir,
            max_clicks=20,
            iou_iter=1,
            compute_box=False,
            distributed=True,
    ):
        self._logger = logging.getLogger(__name__)
        self._dataset_name = dataset_name
        self._distributed = distributed
        self._cpu_device = torch.device("cpu")
        self._output_dir = output_dir

        self.max_clicks = max_clicks
        self.iou_iter = iou_iter
        meta = MetadataCatalog.get(dataset_name)

    def reset(self):
        self.iou_list = []
        self.num_samples = 0
        self.all_ious = [0.5, 0.8, 0.85, 0.9]

    def process(self, inputs, outputs):
        self.iou_list += [o['mask_iou'] for o in outputs]
        self.num_samples += len(outputs)

    def compute_noc(self):
        def _get_noc(iou_arr, iou_thr):
            vals = iou_arr >= iou_thr
            return vals.max(dim=0)[1].item() + 1 if vals.any() else self.max_clicks

        noc_list = {}
        for iou_thr in self.all_ious:
            scores_arr = [_get_noc(iou_arr, iou_thr) for iou_arr in self.iou_list]
            noc_list[str(iou_thr)] = scores_arr

        iou_before_max_iter = torch.stack(self.iou_list)[:,self.iou_iter-1]

        if self._distributed:
            num_samples = sum(all_gather(self.num_samples))
            noc_list_gather = all_gather(noc_list)
            iou_before_max_gather = all_gather(iou_before_max_iter.sum())

            noc_list = {key:[] for key in noc_list_gather[0]}
            for nlg in noc_list_gather:
                for key, value in nlg.items():
                    noc_list[key] += value

        pred_noc = {}
        if self._distributed and (not is_main_process()):
            return pred_noc

        for key, value in noc_list.items():
            assert len(value) == num_samples
            pred_noc[key] = sum(value)*1.0/len(value)

        pred_noc['iou_max_iter'] = sum([x.item() for x in iou_before_max_gather]) / num_samples
        return pred_noc

    def evaluate(self):
        pred_noc = self.compute_noc()

        if self._distributed and (not is_main_process()):
            return

        def draw_iou_curve(iou_list, save_dir):
            iou_list = torch.stack(iou_list, dim=0)
            iou_list = iou_list.mean(dim=0).cpu().numpy()
            # draw iou curve, with x-axis as number of clicks, y-axis as iou using matplotlib
            import matplotlib.pyplot as plt
            plt.figure()
            plt.plot(range(1, self.max_clicks+1), iou_list)
            plt.xlabel('Number of clicks')
            plt.ylabel('IoU')


            # create directory if not exist
            import os
            output_dir = os.path.join(save_dir, 'iou_by_clicks')
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # get current time and format in 10 digits
            import time
            current_time = time.time()
            current_time = int(current_time)
            current_time = str(current_time)

            # save iou curve
            plt.savefig(os.path.join(output_dir, '{}.png'.format(current_time)))

        results = {}
        for idx in range(len(self.all_ious)):
            result_str = 'noc@{}'.format(self.all_ious[idx])
            results[result_str] = pred_noc[str(self.all_ious[idx])]
        
        results['miou@iter{}'.format(self.iou_iter)] = pred_noc['iou_max_iter']
        
        # print("results ", results)
        self._logger.info(results)

        # Save results log to a file
        results_dir = "/results"
        if not os.path.exists(results_dir):
            os.makedirs(results_dir)
        

        # Define the log file path
        log_path = os.path.join(results_dir, "evaluate_result.json")

        # Load existing log results if the file exists
        if os.path.exists(log_path):
            with open(log_path, "r") as log_file:
                log_result = json.load(log_file)
                if log_result is None:
                    log_result = []
        else:
            log_result = []

        # Add a new entry with a timestamp
        log_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "results": results
        }
        log_result.append(log_entry)

        # Save the updated log results back to the file
        with open(log_path, "w") as log_file:
            json.dump(log_result, log_file, indent=4)
        # draw_iou_curve(self.iou_list, self._output_dir)
        return {'interactive': results}

    