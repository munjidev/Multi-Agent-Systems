# Multi-Agent Systems Modeling with Computer Graphics
This is the project repo for the Multi-Agent Systems Modeling with Computer Graphics course. This repo was created in order to host our final project deliverable, which models a small grid resembling a city, with multiple autonomous agents interacting with each other in order to simulate traffic. 

As shown below, each vehicle agent navigates towards its destination building, following road rules such as waiting at a stopsign, changing lanes for turning, and most importantly not crashing into other vehicle agents.

Trello:
https://trello.com/b/hyh2nYDJ/tc2008b-traffic-simulator

Shared Unit:
https://drive.google.com/drive/u/0/folders/0AFf2VcX-DtjFUk9PVA

(replit or .gif goes here)

## Required software

It is necessary to install the Unity editor version 2021.3.13f1 via the Unity Hub. You can [downlaod the hub](https://unity.com/download#how-get-started) via Unity's website.

[Python](https://www.python.org/) is also necessary. We reccommend instlling the [latest version](https://www.python.org/downloads/) via Python's website, or, alternatively, install it via [Anaconda](https://www.anaconda.com/).

In order to make use of the required libraries (mesa and flask), either [Anaconda Distribution](https://www.anaconda.com/products/distribution) or [Miniconda](https://docs.conda.io/en/latest/miniconda.html) must be installed via Anaconda's [website](https://www.anaconda.com/).

We reccommend using [Visual Studio Code](https://code.visualstudio.com/) for straightforward access to the source code, however you may use the IDE of your choice.

**Windows:**

Make sure to downlaod the [.NET core SDK](https://dotnet.microsoft.com/en-us/download) (either .NET versions 6.0 or 7.0). Alternatively, you may download the latest version of [Visual Studio Community](https://visualstudio.microsoft.com/downloads/) and install the SDK by following the installation process.

**MacOS:**

Make sure to have the latest version of [Xcode](https://developer.apple.com/xcode/) installed.

Also, make sure to download the latest version of [Visual Studio Community](https://visualstudio.microsoft.com/downloads/) in order to set up the .NET core SDK via the installation process, as well as a [mono stable release](https://www.mono-project.com/download/stable/) from the [Mono](https://www.mono-project.com/) website.

## Getting started

The current project is based on the Unity editor version 2021.3.12f1 for long term support. As for python, the project uses Python version 3.8, however the project should work with more recent stable versions. For ease of use, [Miniconda](https://docs.conda.io/en/latest/miniconda.html) will be used in order to demonstrate environment setup and library installation.

To get started, make sure to download this repository to your diretory of choice.

In order to setup mesa and flask, make sure to create a conda environment with the following command:

`conda create --name myenv python=3.8`

After creating your environment, open a new terminal, and locate yourself within `~/miniconda3/envs/myenv`. Then, input the following commands:

`pip install mesa`<br />
`pip install flask`

The environment should now have the required libraries for the project to run. When running the project from the terminal, make sure to have the environment activated by writing `conda activate myenv`.

