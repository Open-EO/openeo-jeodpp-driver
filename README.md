# openEO JEODPP web service and back-end

## Work flow

Client posts a job, job is created in the database
![alt text](figures/post_jobs.png "POST /jobs")


Client requests start processing batch job. Job is queued by Kubernetes and status is set to `queued` in database.
![alt text](figures/post_jobs_jobid_results.png "POST /jobs/{jobid}/restults")

Process is started in Kubernetes cluster and status is set to `running` in database.
![alt text](figures/start_process.png "job running")

Process has ended and status is set to `finished` in database.
![alt text](figures/end_process.png "job finished")
