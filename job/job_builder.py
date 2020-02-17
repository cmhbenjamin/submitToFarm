import hou
import fxt.tools.submit_to_farm.job.jobs as jobs
import fxt.tools.submit_to_farm.job.job_errors as error


def job_from_parent(job, parent_job):
    """
    copy basic job attribute from parent node
    :param job:
    :param parent_job:
    :return:
    """

    job.job_name = parent_job.job_name
    job.batch_name = parent_job.batch_name
    job.user_name = parent_job.user_name
    job.machine_name = parent_job.machine_name

    job.department = parent_job.department
    job.comment = parent_job.comment

    job.priority = parent_job.priority
    job.initial_status = parent_job.initial_status

    job.group = parent_job.group
    job.pool = parent_job.pool
    job.secondary_pool = parent_job.secondary_pool

    job.blacklist = parent_job.blacklist
    job.whitelist = parent_job.whitelist

    job.limit_groups = parent_job.limit_groups

    job.extra_info = parent_job.extra_info
    job.override_task_extra_info_names = parent_job.override_task_extra_info_names
    job.task_extra_info_name = parent_job.task_extra_info_name

    job.plugin = parent_job.plugin

    job.override_frame_range = parent_job.override_frame_range
    job.frame_range = parent_job.frame_range

    job.chunk_size_dynamic = parent_job.chunk_size_dynamic
    job.chunk_size_static = parent_job.chunk_size_static
    job.chunk_size = parent_job.chunk_size

    job.scene_path = parent_job.scene_path
    job.output_path = parent_job.output_path

    job.initialized = parent_job.initialized

    job.houdini_job = parent_job.houdini_job
    job.build = parent_job.build
    job.version = parent_job.version

def find_class(node):
    """
    Returns the corresponding deadline job class based on the node type
    :param node:
    :return:
    """
    node_type = node.type().nameComponents()[2]

    if node_type == "dwtv_submit_to_farm":
        return jobs.HoudiniDwtvSubmitToFarmDeadlineJob
    ##########
    # render
    ##########
    if node_type == "ifd":
        return jobs.HoudiniMantraDeadlineJob
    if node_type == "vray_renderer":
        return jobs.HoudiniVRayRendererDeadlineJob
    if node_type == "opengl":
        return jobs.HoudiniOpenglDeadlineJob
    ##########
    # Cache
    ##########
    if node_type == "rop_geometry":
        return jobs.HoudiniRopGeometryDeadlineJob
    if node_type == "rop_dop":
        return jobs.HoudiniRopDopDeadelineJob
    # rop alembic
    if node_type == "rop_alembic":
        return jobs.HoudiniRopAlembicDeadlineJob
    # dwfx_alembic_publish
    if node_type == "dwfx_alembic_cache_publish":
        return jobs.HoudiniRopAlembicDeadlineJob
    if node_type == "filecache":
        return jobs.HoudiniFileCacheDeadlineJob
    # rop fbx
    ##########
    # Sim
    ##########
    if node_type == "wedge":
        return jobs.HoudiniWedgeDeadlineJob
    if node_type == "hq_sim":
        return jobs.HoudiniHqRenderDeadlineJob
    if node_type == "fetch":
        return jobs.HoudiniFetchJob
    ##########
    # Everything else
    ##########

    return None


def job_from_hou_node(job, node):
    def check_parm(node, parm_name):
        """
        :param node:
        :param parm_name:
        :return: parm if it's available , none if not found of disabled
        """
        node.updateParmStates()
        parm = node.parm(parm_name)
        if parm is None:
            return None
        if parm.isDisabled() is True:
            return None
        return parm

    def set_parm(node, job, attr_name, parm_name):
        """
        Set job attribute from node parameter
        :param node:
        :param job:
        :param attr_name:
        :param parm_name:
        :return:
        """
        parm = check_parm(node, parm_name)
        if parm:
            # special data type
            if isinstance(parm.parmTemplate(), hou.ToggleParmTemplate):
                data = bool(parm.eval())
            else:
                data = parm.eval()
            setattr(job, attr_name, data)
            return True
        else:
            return False


    # TODO: attributes to fix: username, machine name, initial_status, plugin
    # set attributes from houdini node if exists
    set_parm(node, job, 'job_name', 'dl_job_name')
    set_parm(node, job, 'batch_name', 'dl_batch_name')
    set_parm(node, job, 'user_name', 'dl_user_name')
    set_parm(node, job, 'machine_name', 'dl_machine_name')

    set_parm(node, job, 'department', 'dl_department')
    set_parm(node, job, 'comment', 'dl_comment')

    set_parm(node, job, 'priority', 'dl_priority')
    set_parm(node, job, 'initial_status', 'dl_initial_status')

    set_parm(node, job, 'group', 'dl_group')
    set_parm(node, job, 'pool', 'dl_pool')
    set_parm(node, job, 'secondary_pool', 'dl_secondary_pool')

    set_parm(node, job, 'blacklist', 'dl_blacklist')
    set_parm(node, job, 'whitelist', 'dl_whitelist')

    set_parm(node, job, 'limit_groups', 'dl_limit_groups')

    set_parm(node, job, 'plugin', 'dl_plugin')
    set_parm(node, job, 'scene_path', 'dl_scene_path')

    set_parm(node, job, 'department', 'dl_department')

    # special parms
    set_parm(node, job, 'override_frame_range', 'dl_override_frame_range')
    set_parm(node, job, 'chunk_size_dynamic', 'dl_chunk_size_dynamic')
    set_parm(node, job, 'chunk_size_static', 'dl_chunk_size_static')
    set_parm(node, job, 'chunk_size', 'dl_chunk_size')
    set_parm(node, job, 'scene_path', 'dl_scene_path')

    # Plugin attributes
    set_parm(node, job, 'version', 'dl_version')
    set_parm(node, job, 'houdini_job', 'dl_houdini_job')
    set_parm(node, job, 'build', 'dl_build')

    job.initialized = True

    # extra infos
    set_parm(node, job, 'override_task_extra_info_names', 'dl_override_task_extra_info_names')
    # TODO: convert to set_parm()
    for i in range(10):
        parm = check_parm(node, 'dl_extra_info_{}'.format(i))
        if parm:
            job.extra_info.append(parm.eval())
        parm = check_parm(node, 'dl_task_extra_info_name_{}'.format(i))
        if parm:
            job.task_extra_info_name.append(parm.eval())

def HoudiniDeadlineJobBuild(node, parent_job=None, job_class=None):
    """
    Generator class to create a job object
    Job object then can be submitted to deadline
    Args:
        node:
        parent_job:
        job_class:

    Returns:

    """

    if job_class is None:
        job_class = find_class(node)
    if not job_class:
        raise error.NodeNotSupported("Error at job building", node)

    job = job_class(node)
    if parent_job:
        job_from_parent(job, parent_job)
    # attribute overwrites from current submission node
    job_from_hou_node(job, node)
    job.update()
    return job

