from prefect.deployments import Deployment
from main_flow import run_pipeline

def deploy():
    deployment = Deployment.build_from_flow(
        flow=run_pipeline,
        name="solana-pipeline-deployment"
    )
    deployment.apply()

if __name__ == '__main__':
   deploy()