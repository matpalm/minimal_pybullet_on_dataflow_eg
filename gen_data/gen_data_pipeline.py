
import argparse
import apache_beam as beam
from apache_beam.io import ReadFromText
from apache_beam.io import WriteToText
from gen_data.renderer import render
import re
import logging


def render_logging_exceptions(render_config):
    # Wrap this in a DoFn if you want to additionally capture Counters
    try:
        return render(render_config)
    except Exception as e:
        logging.error("Error %s" % e)


def run(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', default='seeds.txt')
    parser.add_argument('--output-render-info',
                        default='test_out',
                        help='base path for storing render info (jsons)')
    parser.add_argument('--output-render-png',
                        default="/tmp",
                        help='base path for storing rendered PNGs')
    known_args, pipeline_args = parser.parse_known_args(argv)

    with beam.Pipeline(argv=pipeline_args) as p:

        # collect seeds; one line per pybullet run
        seeds = p | ReadFromText(known_args.input)

        # stitch additional config next to the seed. this could also
        # be done as a stateful DoFn
        render_config = seeds | beam.Map(
            lambda s: (s, known_args.output_render_png))

        # run the renders, but with a wrapper that catches and logs
        # exceptions
        render_infos = render_config | beam.Map(render_logging_exceptions)

        # collect output from renders (json) and write out
        _out = render_infos | WriteToText(known_args.output_render_info)
