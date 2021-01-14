# TODO: from KFP 1.3.0, need to implement for kfp_tekton.compiler

"""Pipeline DSL code for testing URI-based artifact passing."""

from kfp import compiler
from kfp import components
from kfp import dsl


# Patch to make the test result deterministic.
class Coder:
  def __init__(self, ):
    self._code_id = 0

  def get_code(self, ):
    self._code_id += 1
    return '{code:0{num_chars:}d}'.format(
        code=self._code_id,
        num_chars=dsl._for_loop.LoopArguments.NUM_CODE_CHARS)


dsl.ParallelFor._get_unique_id_code = Coder().get_code


write_to_gcs = components.load_component_from_text("""
name: Write to GCS
inputs:
- {name: text, type: String, description: 'Content to be written to GCS'}
outputs:
- {name: output_gcs_path, type: GCSPath, description: 'GCS file path'}
implementation:
  container:
    image: google/cloud-sdk:slim
    command:
    - sh
    - -c
    - |
      set -e -x
      echo "$0" | gsutil cp - "$1"
    - {inputValue: text}
    - {outputUri: output_gcs_path}
""")

read_from_gcs = components.load_component_from_text("""
name: Read from GCS
inputs:
- {name: input_gcs_path, type: GCSPath, description: 'GCS file path'}
implementation:
  container:
    image: google/cloud-sdk:slim
    command:
    - sh
    - -c
    - |
      set -e -x
      gsutil cat "$0"
    - {inputUri: input_gcs_path}
""")


def flip_coin_op():
  """Flip a coin and output heads or tails randomly."""
  return dsl.ContainerOp(
      name='Flip coin',
      image='python:alpine3.6',
      command=['sh', '-c'],
      arguments=['python -c "import random; result = \'heads\' if random.randint(0,1) == 0 '
                 'else \'tails\'; print(result)" | tee /tmp/output'],
      file_outputs={'output': '/tmp/output'}
  )


@dsl.pipeline(
    name='uri-artifact-pipeline',
    output_directory='gs://my-bucket/my-output-dir')
def uri_artifact(text='Hello world!'):
  task_1 = write_to_gcs(text=text)
  task_2 = read_from_gcs(
      input_gcs_path=task_1.outputs['output_gcs_path'])

  # Test use URI within ParFor loop.
  loop_args = [1, 2, 3, 4]
  with dsl.ParallelFor(loop_args) as loop_arg:
    loop_task_2 = read_from_gcs(
        input_gcs_path=task_1.outputs['output_gcs_path'])

  # Test use URI within condition.
  flip = flip_coin_op()
  with dsl.Condition(flip.output == 'heads'):
    condition_task_2 = read_from_gcs(
        input_gcs_path=task_1.outputs['output_gcs_path'])


if __name__ == '__main__':
  compiler.Compiler().compile(uri_artifact, __file__ + '.tar.gz')
