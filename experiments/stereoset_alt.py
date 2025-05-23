import argparse
import json
import os

import transformers

from bias_bench.benchmark.stereoset import StereoSetRunner
from bias_bench.util import generate_experiment_id, _is_generative

# Setup argument parser
thisdir = os.path.dirname(os.path.realpath(__file__))
parser = argparse.ArgumentParser(description="Runs StereoSet benchmark.")

parser.add_argument(
    "--persistent_dir",
    type=str,
    default=os.path.realpath(os.path.join(thisdir, "..")),
    help="Directory where all persistent data will be stored.",
)

parser.add_argument(
    "--model",
    type=str,
    default="AutoModelForMaskedLM",
    help="HuggingFace model class to use (e.g., AutoModelForMaskedLM)."
)

parser.add_argument(
    "--model_name_or_path",
    type=str,
    default="distilroberta-base",
    help="HuggingFace model name or path (e.g., distilroberta-base)."
)

parser.add_argument(
    "--batch_size",
    type=int,
    default=1,
    help="The batch size to use during StereoSet intrasentence evaluation.",
)

parser.add_argument(
    "--seed",
    type=int,
    default=None,
    help="RNG seed. Used for logging in experiment ID.",
)

# Main entry
if __name__ == "__main__":
    args = parser.parse_args()

    experiment_id = generate_experiment_id(
        name="stereoset",
        model=args.model,
        model_name_or_path=args.model_name_or_path,
        seed=args.seed,
    )

    print("Running StereoSet:")
    print(f" - persistent_dir: {args.persistent_dir}")
    print(f" - model: {args.model}")
    print(f" - model_name_or_path: {args.model_name_or_path}")
    print(f" - batch_size: {args.batch_size}")
    print(f" - seed: {args.seed}")

    # Dynamically load model and tokenizer
    model_cls = getattr(transformers, args.model)
    model = model_cls.from_pretrained(args.model_name_or_path)
    model.eval()
    tokenizer = transformers.AutoTokenizer.from_pretrained(args.model_name_or_path)

    # Run StereoSet benchmark
    runner = StereoSetRunner(
        intrasentence_model=model,
        tokenizer=tokenizer,
        input_file=f"{args.persistent_dir}/data/stereoset/test.json",
        model_name_or_path=args.model_name_or_path,
        batch_size=args.batch_size,
        is_generative=_is_generative(args.model),
    )
    results = runner()

    # Save results
    os.makedirs(f"{args.persistent_dir}/results/stereoset", exist_ok=True)
    with open(
        f"{args.persistent_dir}/results/stereoset/{experiment_id}.json", "w"
    ) as f:
        json.dump(results, f, indent=2)
