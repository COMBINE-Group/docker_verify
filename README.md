# Setting up
[install docker first](https://docs.docker.com/engine/install/).

# How to install MVT

1. Download the latest available release from [here](https://github.com/COMBINE-Group/docker_verify/releases)
2. open a command line, and then: `docker load -i MVT_vX.X.X.tar.gz`, replace the `X` with the latest versione of MVT.
3. after that, run this command in your command line `docker run -d -p 8000:8000 model_verification_tools:vX.X.X` replace the `X` with the latest versione of MVT.
4. Open in your browser this link: 0.0.0.0:8000


![Schema MVT](https://user-images.githubusercontent.com/4471950/131531984-0b28ae13-f8da-49e8-aa9f-6d71692706ec.jpg)

