from sqlalchemy.orm import Session
from sqlalchemy.orm import Query
import subprocess


from .. import models


def get_job_process_graph(
    *,
    db_session: Session,
    job_id: str,
) -> Query:
    """ Return a Job.proces.process_graph Query. """
    query = db_session.query(models.Job.process["process_graph"]).filter(
        models.Job.id == job_id
    )
    job_process_graph = query.one_or_none()
    return job_process_graph


def get_job_status(
    *,
    db_session: Session,
    job_id: str,
) -> Query:
    """ Return a Job.status Query. """
    query = db_session.query(models.Job).filter(models.Job.id == job_id)
    job_status = query.one_or_none()
    return job_status.status


def update_job_status(
    *, db_session: Session, job_id: str, job_status: models.job.ProcessStatus
) -> None:
    """ Update a Job.status Query. """
    db_session.query(models.Job).filter(models.Job.id == job_id).update(
        {"status": job_status}
    )
    db_session.commit()


def add_job_to_queue(db_session: Session, job_id: str):
    """ Function to add job to a k8s / htcondor queue """
    try:
        print("starting kubectl exec")
        path = '/scratch2/kempepi'
        #this is working for old image:
        # subprocess.call(["/bin/bash", "-c", "kubectl exec -n openeo openeotest-6589984f8-9vxft -- python3 /home/install/openeo-master-cd09b74ea9eab60d60c225d9a843bfc9538a2c81/back_end/run_test.py"])
        subprocess.call(["/bin/bash", "-c", "kubectl exec -n openeo openeotest-6589984f8-9vxft -- python3 /home/install/openeo-master-cd09b74ea9eab60d60c225d9a843bfc9538a2c81/back_end/run.py -job_id " + job_id + " -path " + path])
        update_job_status(db_session=db_session, job_id=job_id, job_status=models.job.ProcessStatus.queued)
    except:
        update_job_status(db_session, job_id, models.job.ProcessStatus.error)
    return k8s_job_status

def is_job_running_in_k8s(job_id: str):
    return True


def remove_job_from_k8s(job_id: str):
    return True


def remove_job_from_queue(db_session: Session, job_id: str):
    """ Check if job is running in k8s and has job_status == 'running' in db """
    job_status_k8s = is_job_running_in_k8s(job_id)
    if is_job_running_in_k8s is True:
        """ Funtion to remove the job from K8S queue """
        remove_job_k8s = remove_job_from_k8s(job_id)
        if remove_job_k8s is True:
            update_job_status(
                db_session=db_session, job_id=job_id, job_status="canceled"
            )
    else:
        update_job_status(db_session=db_session, job_id=job_id, job_status="created")
    job_status_db = get_job_status(db_session=db_session, job_id=job_id)
    return job_status_db


def job_estimate(job_id: str):
    job_estimate = {
        "costs": 12.98,
        "duration": "P1Y2M10DT2H30M",
        "size": 157286400,
        "downloads_included": 5,
        "expires": "2020-11-01T00:00:00Z",
    }
    return job_estimate
