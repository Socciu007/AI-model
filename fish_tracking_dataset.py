import datasets
import pandas as pd

_CITATION = """\
@InProceedings{huggingface:dataset,
title = {fish-tracking-dataset},
author = {TrainingDataPro},
year = {2023}
}
"""

_DESCRIPTION = """\
The collection of video frames, capturing various types of fish swimming in the water.
The dataset includes fish of different colors, sizes and with different swimming speeds.
"""
_NAME = "fish-tracking-dataset"

_HOMEPAGE = f"https://huggingface.co/datasets/TrainingDataPro/{_NAME}"

_LICENSE = ""

_DATA = f"https://huggingface.co/datasets/TrainingDataPro/{_NAME}/resolve/main/data/"


class FishTrackingDataset(datasets.GeneratorBasedBuilder):
  def _info(self):
    return datasets.DatasetInfo(
      description=_DESCRIPTION,
      features=datasets.Features(
        {
          "id": datasets.Value("int32"),
          "image": datasets.Image(),
          "mask": datasets.Image(),
          "bboxes": datasets.Value("string"),
        }
      ),
      supervised_keys=None,
      homepage=_HOMEPAGE,
      citation=_CITATION,
    )

  def _split_generators(self, dl_manager):
    images = dl_manager.download(f"{_DATA}images.tar.gz")
    masks = dl_manager.download(f"{_DATA}boxes.tar.gz")
    annotations = dl_manager.download(f"{_DATA}{_NAME}.csv")
    images = dl_manager.iter_archive(images)
    masks = dl_manager.iter_archive(masks)
    return [
      datasets.SplitGenerator(
        name=datasets.Split.TRAIN,
        gen_kwargs={
          "images": images,
          "masks": masks,
          "annotations": annotations,
        },
    ),
    ]

  def _generate_examples(self, images, masks, annotations):
    annotations_df = pd.read_csv(annotations)

    for idx, ((image_path, image), (mask_path, mask)) in enumerate(zip(images, masks)):
      yield idx, {
        "id": annotations_df["image_id"].iloc[idx],
        "image": {"path": image_path, "bytes": image.read()},
        "mask": {"path": mask_path, "bytes": mask.read()},
        "bboxes": annotations_df["annotations"].iloc[idx],
      }