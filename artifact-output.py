from kfp import dsl
from kubernetes.client.models import V1SecretKeySelector


@dsl.pipeline(name='artifact-location-pipeine', description='hello world')
def foo_pipeline(tag: str, namespace: str = "kubeflow", bucket: str = "foobar"):

    # configures artifact location
    pipeline_artifact_location = dsl.ArtifactLocation.s3(
                            bucket=bucket,
                            endpoint="minio-service.%s:9000" % namespace,
                            insecure=True,
                            access_key_secret={"name": "minio", "key": "accesskey"},
                            secret_key_secret=V1SecretKeySelector(name="minio", key="secretkey"))

    # configures artifact location using AWS IAM role (no access key provided)
    aws_artifact_location = dsl.ArtifactLocation.s3(
                            bucket=bucket,
                            endpoint="s3.amazonaws.com",
                            region="ap-southeast-1",
                            insecure=False)

    # set pipeline level artifact location
    dsl.get_pipeline_conf().set_artifact_location(pipeline_artifact_location)

    # pipeline level artifact location (to minio)
    op1 = dsl.ContainerOp(
        name='foo', 
        image='busybox:%s' % tag,
        output_artifact_paths={
            'out_art': '/tmp/out_art.txt',
        },
    )
