from absl import flags
from speciesnet.scripts import run_model

flags.FLAGS(['run_model'])

flags.FLAGS.filepaths = "test_images/2022-09-20 17-30-09.JPG"
flags.FLAGS.country = "POL"
flags.FLAGS.progress_bars = False
flags.FLAGS.predictions_json = "e_predictions.json"

results = run_model.main(['run_model'])

print(results)
