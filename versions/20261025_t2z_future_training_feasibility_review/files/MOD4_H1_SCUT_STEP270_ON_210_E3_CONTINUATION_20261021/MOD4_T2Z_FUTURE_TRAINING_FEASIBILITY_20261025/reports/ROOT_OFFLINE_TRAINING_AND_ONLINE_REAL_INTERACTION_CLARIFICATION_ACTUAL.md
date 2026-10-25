# Clarification: offline24-hour training and real-interaction test-time adaptation

The human asked whether the method learns from recordings or instead feeds the data from one real arm dragging action into the world model. These describe different parts of the same pipeline. The recorded input is not arbitrary passive video: it is paired real interaction observations and synchronized robot actions.

Offline, many such recorded trajectories from varied environments are used to train the pretrained task world model and environment representations in alternating phases. The paper reports2 H200 GPUs for24 hours per common task/method, not a robot policy PPO training budget.

At a new environment, the arm actually executes one or a few interactions. Initial/subsequent RGB frames and the executed actions are observed. The model prediction is compared with the observed consequence, and backpropagation updates only the new32-dimensional environment latent while shared model weights remain frozen. This is a valid interpretation of using one real trial and feeding its data back. It does not mean directly inverting video into a correct control action. Once adapted, the model predicts futures for candidate actions, which are scored/compared before executing a selected action.

The18.09-second H200 result includes40 latent updates plus five query-video generations, excluding loading/data reads/video writing. It is not the isolated adaptation time or a measured4090 result.

Primary sources: https://arxiv.org/html/2610.22364v1#S3 and https://github.com/T2-z-latent-optimization/T2-z/blob/c72f051f5cffcb1f372a32bc488df273556d39b9/README.md . This clarification is read-only; no data/model download, code execution, rollout, training, actor-input change or budget write occurred.
