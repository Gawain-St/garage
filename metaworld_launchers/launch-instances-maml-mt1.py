import subprocess
import os

algorithm ='maml-trpo'
sub_experiment_type = 'mamled-baseline'
experiment_type = f'mt1-pick-place-tuning-{sub_experiment_type}'
num_experiments = 3
zone = 'us-central1-a'
machine_type = 'n2-standard-8'
source_machine_image = 'metaworld-v2-cpu-instance'
bucket = f'mt1-pick-place-maml-tuning/{sub_experiment_type}'
branch='avnish-maml-mlp-baseline'

entropy_coeff = [5e-6, 5e-5, 1e-4]
for i in range(num_experiments):
    script = (
f'''#!/bin/bash
cd /home/avnishnarayan/
rm -rf garage/
rm -rf metaworld-runs-v2
runuser -l avnishnarayan -c "git clone https://github.com/rlworkgroup/garage && cd garage/ && git checkout {branch} && mkdir data/"
runuser -l avnishnarayan -c "mkdir -p metaworld-runs-v2/local/experiment/"
runuser -l avnishnarayan -c "make run-headless -C ~/garage/"
runuser -l avnishnarayan -c "cd garage && python docker_metaworld_run_cpu.py 'metaworld_launchers/mt1/maml_trpo_metaworld_mt1.py --env-name pick-place-v2 --entropy_coefficient {entropy_coeff[i]}'"
runuser -l avnishnarayan -c "cd garage/metaworld_launchers && python upload_folders.py {bucket} 1200"''')
    with open(f'launch-experiment-maml-mt1-{i}.sh', mode='w') as f:
        f.write(script)
    subprocess.Popen([f"gcloud beta compute instances create {algorithm}-{experiment_type}-{i} --metadata-from-file startup-script=launch-experiment-maml-mt1-{i}.sh --zone {zone} --source-machine-image {source_machine_image} --machine-type {machine_type}"], shell=True)