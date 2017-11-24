# pgTK90 - DRL on Spectrum console

## What is it?

pgTK90 was our end-of-career project as Engeneer students. Some days ago we approved it, and since then our country has two Engineers more (and one more coming soon!). So now we are sharing 'our' code. Our final report is also available [here](https://www.fing.edu.uy/inco/grupos/pln/prygrado/informe_pgtk90.pdf).

Our main contribution is the environment developed for Spectrum console, and in particular, for Manic Miner.

We took the work of Matthias Plappert [1](https://github.com/matthiasplappert) as reference for the Agent and used OpenAI GYM [2](https://github.com/openai/gym) as reference to implement the environment.

In adition to the work done by Matthias Plappert for the agent, we implemented:

* Prioritized Experience Replay [PER](https://arxiv.org/pdf/1511.05952.pdf)
* Human Checkpoint Replay [HCR](https://arxiv.org/pdf/1607.05077.pdf)


With the environment we developed an interactive console to play the game over the effects of frame skipping, save checkpoints (which can also be used to train with HCR) and edit and save levels (this is useful to test the capacity of the agent to generalize its knowledge)

We are updating this code (and documentation) since this work was recently finished

## TODOs:
* update documentation
* add examples
