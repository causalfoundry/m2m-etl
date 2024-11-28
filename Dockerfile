# syntax=docker/dockerfile:1
FROM mambaorg/micromamba:2.0.4

RUN micromamba install -n base -c conda-forge -y     \
        "python>=3.11"                               \
        pip                                          \
        setuptools                                   \
        cython                                       \
        numba                                        \
        numpy                                        \
        nomkl                                        \
        scipy                                        \
        pandas                                       \
        "scikit-learn>=1.2"                          \
        pytest                                       

RUN micromamba clean --all --yes

ARG MAMBA_DOCKERFILE_ACTIVATE=1

WORKDIR /etl
COPY ./src ./

USER root
USER mambauser

CMD ["python", "main.py"]
