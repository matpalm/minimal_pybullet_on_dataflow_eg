"""
run locally

python3 gen_data_main.py \
  --input ./seeds.txt \
  --output-render-png /tmp \
  --output-render-info render_info

run on dataflow

export PROJECT=YOUR_PROJECT
export BUCKET=YOUR_BUCKET
gsutil cp seeds.txt gs://$BUCKET/gen_data/
python3 gen_data_main.py \
  --job_name gen-data-$USER \
  --project $PROJECT \
  --runner DataflowRunner \
  --setup_file ./setup.py \
  --staging_location gs://$BUCKET/_staging \
  --temp_location gs://$BUCKET/_tmp \
  --input gs://$BUCKET/gen_data/seeds.txt \
  --output-render-png gs://$BUCKET/gen_data/renders \
  --output-render-info gs://$BUCKET/gen_data/render_info
"""

import logging

from gen_data import gen_data_pipeline

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    gen_data_pipeline.run()
