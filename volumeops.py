import kfp.dsl as dsl


@dsl.pipeline(
    name="VolumeOp Basic",
    description="A Basic Example on VolumeOp Usage."
)
def volumeop_basic(size):
    vop = dsl.VolumeOp(
        name="create_pvc",
        resource_name="my-pvc",
        modes=dsl.VOLUME_MODE_RWM,
        size=size
    )

    cop = dsl.ContainerOp(
        name="cop",
        image="library/bash:4.4.23",
        command=["sh", "-c"],
        arguments=["echo foo > /mnt/file1"],
        pvolumes={"/mnt": vop.volume}
    )


if __name__ == "__main__":
    import kfp.compiler as compiler
    compiler.Compiler().compile(volumeop_basic, __file__ + ".tar.gz")
